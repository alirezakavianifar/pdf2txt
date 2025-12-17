
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
            "بدهکاری": ["بدهکاری"],
            "کسر هزار ریال": ["کسر هزار ریال"],
        }
        
        # Iterate over text to find matches
        # Note: Text extraction might lose newlines or visual layout structure.
        # We try finding keys and subsequent values.
        
        # Simplified loop: check each pattern against full text or lines
        # Using full text search for robustness
        
        normalized_text = " ".join(lines)
        
        for key, search_terms in keys_map.items():
            for term in search_terms:
                # Try Key Value
                pattern1 = rf'{term}[:\s]*([\d,/\.]+)'
                match = re.search(pattern1, normalized_text)
                
                # Try Value Key
                pattern2 = rf'([\d,/\.]+)\s*{term}'
                match2 = re.search(pattern2, normalized_text)
                
                value_str = None
                if match:
                    value_str = match.group(1)
                elif match2:
                    value_str = match2.group(1)
                
                if value_str:
                    # Filter out if it's just punctuation
                    if not any(c.isdigit() for c in value_str):
                        continue
                        
                    # Handle dates
                    if "تاریخ" in key and "تعداد" not in key:
                         # verify Date format
                         if re.search(r'\d{4}/\d{2}/\d{2}', value_str):
                             result["اطلاعات ترانزیت"][key] = value_str
                             break
                    elif "دوره/سال" in key:
                         if re.search(r'\d{4}/\d{2}', value_str) or re.search(r'\d{2}/\d{2}', value_str):
                              result["اطلاعات ترانزیت"][key] = value_str
                              break
                    else:
                        # Numeric
                        if key == "ترانزیت" and "نرخ" in normalized_text and "نرخ" not in term:
                             # Prevent "Transit" from matching "Monthly Transit Rate"
                             # But here we search specifically for "Transit" term
                             # If "Transit" is prefix of "Transit Rate", simple regex might pick up the rate if not careful
                             # But here we consume the number next to it.
                             pass
                        
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
