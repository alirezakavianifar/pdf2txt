
import json
import re
import sys
from pathlib import Path

def parse_decimal_number(text):
    if not text:
        return None
    # Remove commas
    clean_text = text.replace(',', '')
    # Handle slash as decimal if appropriate (context dependent, usually dot)
    # But for "1404/01/01" it's a date.
    if '/' in clean_text and len(clean_text) < 10: # heuristic (dates are longer or have specific format)
        clean_text = clean_text.replace('/', '.')
        
    try:
        return float(clean_text)
    except ValueError:
        return None

def restructure_transit_section_json(input_json_path, output_json_path):
    """Restructure transit section JSON."""
    try:
        with open(input_json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        text = data.get('text', '')
        
        # Initialize result
        result = {
            "اطلاعات ترانزیت": {
                "از تاریخ": None,
                "تا تاریخ": None,
                "تعداد روز دوره": None,
                "دوره/سال": None,
                "ضریب زیان": None,
                "قدرت مشمول ترانزیت": None,
                "نرخ ماهیانه ترانزیت": None,
                "ترانزیت": None,
                "مالیات بر ارزش افزوده": None,
                "جمع دوره": None,
                "بدهکاری": None,
                "کسر هزار ریال": None
            }
        }
        
        # Guard clause: Check if it's actually a transit section
        # If "ترانزیت" or "حق العمل" is not in text, assume it's not a transit section
        if "ترانزیت" not in text and "حق العمل" not in text and "Transit" not in text:
             with open(output_json_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
             return result
        
        lines = text.split('\n')
        
        # Regex map
        # Regex map: supporting both "Key Value" and "Value Key"
        # We'll use a specific helper for this
        keys_map = {
            "از تاریخ": ["از تاریخ"],
            "تا تاریخ": ["تا تاریخ"],
            "تعداد روز دوره": ["تعداد روز دوره"],
            "دوره/سال": ["دوره/سال"],
            "ضریب زیان": ["ضریب زیان"],
            "قدرت مشمول ترانزیت": ["قدرت مشمول ترانزیت"],
            "نرخ ماهیانه ترانزیت": ["نرخ ماهیانه ترانزیت"],
            "ترانزیت": ["ترانزیت"], # Might match "نرخ ماهیانه ترانزیت", so check order or exclude matching longer one
            "مالیات بر ارزش افزوده": ["مالیات بر ارزش افزوده"],
            "جمع دوره": ["جمع دوره"],
            "بدهکاری": ["بدهکاری", "بستانکاری"],
            "کسر هزار ریال": ["کسر هزار ریال"],
        }
        
        # Iterate over text to find matches
        # Note: Text extraction might lose newlines or visual layout structure.
        # We try finding keys and subsequent values.
        
        for line in lines:
            normalized_line = line.strip()
            if not normalized_line:
                continue
                
            for key, search_terms in keys_map.items():
                if result["اطلاعات ترانزیت"].get(key): # Already found
                    continue
                    
                for term in search_terms:
                    # Check if term is in line
                    if term not in normalized_line:
                        continue
                        
                    # Special handling for "بدهکاری" when on same line as "دوره/سال"
                    if key == "بدهکاری" and "دوره/سال" in normalized_line:
                        parts = normalized_line.split()
                        found_val = None
                        for p in parts:
                            p_clean = p.replace(',', '')
                            if re.match(r'^\d+$', p_clean):
                                found_val = parse_decimal_number(p_clean)
                                break
                        if found_val is not None:
                            result["اطلاعات ترانزیت"][key] = found_val
                            break

                    # Special handling for "قدرت مشمول ترانزیت" when on same line as "کسر هزار ریال"
                    if key == "قدرت مشمول ترانزیت" and "کسر هزار ریال" in normalized_line:
                        nums = re.findall(r'[\d,.]+', normalized_line)
                        nums = [n for n in nums if re.match(r'^[\d,.]+$', n) and '/' not in n]
                        if len(nums) >= 2:
                             # Heuristic: [Power, Deduction] -> `0.05 251`
                             pow_val = parse_decimal_number(nums[0])
                             ded_val = parse_decimal_number(nums[-1])
                             
                             result["اطلاعات ترانزیت"][key] = pow_val
                             # Set Deduction too since we are here
                             result["اطلاعات ترانزیت"]["کسر هزار ریال"] = ded_val
                             break

                    # Special handling for "کسر هزار ریال" when on same line as "قدرت"
                    if key == "کسر هزار ریال" and "قدرت" in normalized_line:
                        # Fix regex to include dot for decimals
                        nums = re.findall(r'[\d,.]+', normalized_line)
                        # Filter valid numbers (exclude ones with slash usually dates, though dot handled in parse)
                        nums = [n for n in nums if re.match(r'^[\d,.]+$', n) and '/' not in n]
                        
                        if len(nums) >= 2:
                            # Heuristic: [Power, Deduction] usually in that order `22.4 778 - ...`
                            # Assign both if possible
                            pow_val = parse_decimal_number(nums[0])
                            ded_val = parse_decimal_number(nums[-1]) # Use last for deduction
                            
                            result["اطلاعات ترانزیت"][key] = ded_val
                            # Always overwrite Power with confident values from this specific layout
                            result["اطلاعات ترانزیت"]["قدرت مشمول ترانزیت"] = pow_val
                            break
                        elif len(nums) == 1:
                            # Only one number found?
                            # If we already have Power, this might be Deduction
                            if result["اطلاعات ترانزیت"]["قدرت مشمول ترانزیت"]:
                                result["اطلاعات ترانزیت"][key] = parse_decimal_number(nums[0])
                            else:
                                # Ambiguous. If it's float, maybe Power. If int, maybe Deduction.
                                val = parse_decimal_number(nums[0])
                                if val is not None and val < 1000 and float(val).is_integer():
                                     result["اطلاعات ترانزیت"][key] = val
                                else:
                                     # Assuming it matches the key we are looking for (Ksr)
                                     result["اطلاعات ترانزیت"][key] = val
                            break

                    # Try Value Key (Number then Term)
                    pattern_val_key = rf'([\d,/\.]+)\s*{re.escape(term)}'
                    match_val_key = re.search(pattern_val_key, normalized_line)
                    
                    # Try Key Value (Term then Number)
                    pattern_key_val = rf'{re.escape(term)}[:\s]*([\d,/\.]+)'
                    match_key_val = re.search(pattern_key_val, normalized_line)
                    
                    value_str = None
                    if match_val_key:
                        value_str = match_val_key.group(1)
                    elif match_key_val:
                        value_str = match_key_val.group(1)
                    
                    if value_str:
                         # Filter out unwanted chars or check validity
                         if not any(c.isdigit() for c in value_str):
                             continue
                        
                         # Handle dates
                         if "تاریخ" in key and "تعداد" not in key:
                             if re.search(r'\d{4}/\d{2}/\d{2}', value_str):
                                 result["اطلاعات ترانزیت"][key] = value_str
                                 break
                         elif "دوره/سال" in key:
                             if re.search(r'\d{4}/\d{2}', value_str) or re.search(r'\d{2}/\d{2}', value_str):
                                  result["اطلاعات ترانزیت"][key] = value_str
                                  break
                         else:
                             # Numeric
                             if key == "ترانزیت" and "نرخ" in normalized_line and "نرخ" not in term:
                                 continue
                             
                             parsed = parse_decimal_number(value_str)
                             if parsed is not None:
                                 result["اطلاعات ترانزیت"][key] = parsed
                                 break
                    
        # Fallback: if regex fails due to spacing (e.g. "ترانزیت 89,484,600"), try simpler proximity
        # The screenshot shows value on left/right of label.
        
        # Saving
        with open(output_json_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
            
        return result

    except Exception as e:
        print(f"Error structuring transit section: {e}")
        return None

if __name__ == "__main__":
    if len(sys.argv) > 2:
        restructure_transit_section_json(sys.argv[1], sys.argv[2])
