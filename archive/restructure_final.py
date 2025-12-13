"""Final restructure script using table data directly."""
import json
from pathlib import Path
from typing import Dict, List, Any


def parse_number(value: str) -> Any:
    """Parse number from string, handling commas."""
    if not value or value == '':
        return 0
    try:
        return int(value.replace(',', '').strip())
    except ValueError:
        try:
            return float(value.replace(',', '').strip())
        except ValueError:
            return value


def restructure_json(input_path: Path, output_path: Path):
    """Restructure JSON from extraction format to desired format."""
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    table_rows = data['table']['rows']
    
    # Known row indices based on the structure (we'll find them by content)
    results = {
        "شرح مصارف": [],
        "مابه التفاوت ماده 16": {"جهش تولید": {}},
        "مابه التفاوت اجرای مقررات": [],
        "جمع": {}
    }
    
    # Find rows by looking for Persian keywords in the row text
    def find_row_idx(keywords):
        for i, row in enumerate(table_rows):
            row_text = ' '.join(str(cell) if cell else '' for cell in row)
            if any(kw in row_text for kw in keywords):
                return i, row
        return None, None
    
    # Extract upper table data
    # Row 1 (index 1): میان باری - "140,026,901", "4063.462", "34460 0 0", "34460", "1758899", "1724439", "میان باری"
    idx, row = find_row_idx(['میان باری'])
    if row:
        # Extract numbers from the row - filter out empty strings
        values = [cell for cell in row if cell and str(cell).strip()]
        # Based on the structure: amount, rate, energy_savings, energy_included, curr_meter, prev_meter, description
        if len(values) >= 7:
            results["شرح مصارف"].append({
                "شرح مصارف": "میان باری",
                "TOU": 13,
                "شماره کنتور قبلی": parse_number(str(values[5])),
                "شماره کنتور کنونی": parse_number(str(values[4])),
                "ضریب": 1,
                "مصرف کل": parse_number(str(values[3])),
                "گواهی صرفه جویی": {
                    "تولید": 0,
                    "خرید": 0,
                    "دوجانبه": 0,
                    "بورس": 0
                },
                "بهای انرژی پشتیبانی شده": {
                    "انرژی مشمول": parse_number(str(values[3])),
                    "نرخ": float(str(values[1])),
                    "مبلغ (ریال)": parse_number(str(values[0]))
                }
            })
    
    # Row 2: اوج باری
    idx, row = find_row_idx(['اوج باری'])
    if row:
        values = [cell for cell in row if cell and str(cell).strip()]
        if len(values) >= 7:
            results["شرح مصارف"].append({
                "شرح مصارف": "اوج باری",
                "TOU": 2,
                "شماره کنتور قبلی": parse_number(str(values[5])),
                "شماره کنتور کنونی": parse_number(str(values[4])),
                "ضریب": 1,
                "مصرف کل": parse_number(str(values[3])),
                "گواهی صرفه جویی": {
                    "تولید": 0,
                    "خرید": 0,
                    "دوجانبه": 0,
                    "بورس": 0
                },
                "بهای انرژی پشتیبانی شده": {
                    "انرژی مشمول": parse_number(str(values[3])),
                    "نرخ": float(str(values[1])),
                    "مبلغ (ریال)": parse_number(str(values[0]))
                }
            })
    
    # Row 3: کم باری
    idx, row = find_row_idx(['کم باری'])
    if row:
        values = [cell for cell in row if cell and str(cell).strip()]
        if len(values) >= 7:
            results["شرح مصارف"].append({
                "شرح مصارف": "کم باری",
                "TOU": 9,
                "شماره کنتور قبلی": parse_number(str(values[5])),
                "شماره کنتور کنونی": parse_number(str(values[4])),
                "ضریب": 1,
                "مصرف کل": parse_number(str(values[3])),
                "گواهی صرفه جویی": {
                    "تولید": 0,
                    "خرید": 0,
                    "دوجانبه": 0,
                    "بورس": 0
                },
                "بهای انرژی پشتیبانی شده": {
                    "انرژی مشمول": parse_number(str(values[3])),
                    "نرخ": float(str(values[1])),
                    "مبلغ (ریال)": parse_number(str(values[0]))
                }
            })
    
    # Row 4: اوج بار جمعه
    idx, row = find_row_idx(['اوج بار جمعه'])
    if row:
        values = [cell for cell in row if cell and str(cell).strip()]
        if len(values) >= 7:
            results["شرح مصارف"].append({
                "شرح مصارف": "اوج بار جمعه",
                "TOU": 0,
                "شماره کنتور قبلی": parse_number(str(values[5])),
                "شماره کنتور کنونی": parse_number(str(values[4])),
                "ضریب": 1,
                "مصرف کل": parse_number(str(values[3])),
                "گواهی صرفه جویی": {
                    "تولید": 0,
                    "خرید": 0,
                    "دوجانبه": 0,
                    "بورس": 0
                },
                "بهای انرژی پشتیبانی شده": {
                    "انرژی مشمول": parse_number(str(values[3])),
                    "نرخ": float(str(values[1])),
                    "مبلغ (ریال)": parse_number(str(values[0]))
                }
            })
    
    # Total row (جمع)
    idx, row = find_row_idx(['جمع'])
    if row:
        values = [cell for cell in row if cell and str(cell).strip()]
        # Find the total amount and consumption
        amounts = [parse_number(str(v)) for v in values if isinstance(parse_number(str(v)), int) and parse_number(str(v)) > 1000000]
        consumptions = [parse_number(str(v)) for v in values if isinstance(parse_number(str(v)), int) and 10000 < parse_number(str(v)) < 100000]
        if amounts and consumptions:
            results["جمع"] = {
                "مصرف کل": consumptions[0],
                "مبلغ (ریال)": amounts[0]
            }
    
    # Extract lower table data (مابه التفاوت اجرای مقررات)
    # These appear in rows around index 9-12 based on the JSON structure
    # Row with "میان باری" and "29,613,201"
    for i, row in enumerate(table_rows):
        row_text = ' '.join(str(cell) if cell else '' for cell in row)
        if 'میان باری' in row_text and '2617.65' in row_text:
            values = [cell for cell in row if cell and str(cell).strip()]
            nums = [parse_number(str(v)) for v in values]
            nums = [n for n in nums if isinstance(n, (int, float)) and n > 0]
            if len(nums) >= 5:
                results["مابه التفاوت اجرای مقررات"].append({
                    "شرح مصارف": "میان باری",
                    "انرژی مشمول": int(nums[0]),
                    "نرخ پایه": float(nums[1]),
                    "متوسط نرخ بازار": float(nums[2]),
                    "تفاوت نرخ": float(nums[3]),
                    "مبلغ (ریال)": int(nums[4])
                })
        
        elif 'اوج باری' in row_text and '2617.65' in row_text and '40,076,547' in row_text:
            values = [cell for cell in row if cell and str(cell).strip()]
            nums = [parse_number(str(v)) for v in values]
            nums = [n for n in nums if isinstance(n, (int, float)) and n > 0]
            if len(nums) >= 5:
                results["مابه التفاوت اجرای مقررات"].append({
                    "شرح مصارف": "اوج باری",
                    "انرژی مشمول": int(nums[0]),
                    "نرخ پایه": float(nums[1]),
                    "متوسط نرخ بازار": float(nums[2]),
                    "تفاوت نرخ": float(nums[3]),
                    "مبلغ (ریال)": int(nums[4])
                })
        
        elif 'کم باری' in row_text and '2617.65' in row_text:
            values = [cell for cell in row if cell and str(cell).strip()]
            nums = [parse_number(str(v)) for v in values]
            nums = [n for n in nums if isinstance(n, (int, float)) and n > 0]
            if len(nums) >= 3:
                results["مابه التفاوت اجرای مقررات"].append({
                    "شرح مصارف": "کم باری",
                    "انرژی مشمول": int(nums[0]),
                    "نرخ پایه": float(nums[1]),
                    "متوسط نرخ بازار": float(nums[2]),
                    "تفاوت نرخ": 0,
                    "مبلغ (ریال)": 0
                })
        
        elif 'اوج بار جمعه' in row_text and '2617.65' in row_text:
            values = [cell for cell in row if cell and str(cell).strip()]
            nums = [parse_number(str(v)) for v in values]
            nums = [n for n in nums if isinstance(n, (int, float)) and n > 0]
            if len(nums) >= 5:
                results["مابه التفاوت اجرای مقررات"].append({
                    "شرح مصارف": "اوج بار جمعه",
                    "انرژی مشمول": int(nums[0]),
                    "نرخ پایه": float(nums[1]),
                    "متوسط نرخ بازار": float(nums[2]),
                    "تفاوت نرخ": float(nums[3]),
                    "مبلغ (ریال)": int(nums[4])
                })
    
    # Save output
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"Restructured data saved to: {output_path}")
    print(f"  - شرح مصارف: {len(results['شرح مصارف'])} items")
    print(f"  - مابه التفاوت اجرای مقررات: {len(results['مابه التفاوت اجرای مقررات'])} items")
    
    return results


if __name__ == "__main__":
    input_file = Path("output/1_cropped_test.json")
    output_file = Path("output/1_cropped_restructured.json")
    
    result = restructure_json(input_file, output_file)
    
    # Write sample to file for verification
    sample_file = Path("output/sample_output.json")
    with open(sample_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
