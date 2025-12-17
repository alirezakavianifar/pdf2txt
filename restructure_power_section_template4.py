
from pathlib import Path
import json
import re
from text_normalization import default_normalizer

def parse_decimal_number(text):
    """Parse a number string, removing commas and handling Persian format."""
    if not text:
        return None
    # Remove commas and spaces
    clean = text.replace(',', '').replace(' ', '').strip()
    try:
        return float(clean)
    except ValueError:
        return None

def restructure_power_section_template4_json(json_path: Path, output_path: Path):
    """
    Restructures the Power Section (Template 4) JSON output.
    Extracts: قراردادی (Contractual), پروانه مجاز (Licensed), مصرفی (Consumed), 
    محاسبه شده (Calculated), کاهش یافته (Reduced), تجاوز از قدرت (Excess Power).
    """
    print(f"Restructuring Power Section (Template 4) from {json_path}...")
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # Get text from both text field and table
        text = data.get("text", "")
        table_data = data.get("table", {})
        
        # Also check table rows for power section data
        if table_data and "rows" in table_data:
            for row in table_data["rows"]:
                for cell in row:
                    if cell and isinstance(cell, str) and ("قراردادی" in cell or "پروانه مجاز" in cell or "مصرفی" in cell):
                        text += "\n" + cell
        
        # Normalize text (don't apply BIDI to preserve number order)
        text = default_normalizer.normalize(text, apply_bidi=False)
        lines = text.split('\n')
        
        # Initialize result with Persian field names
        result = {
            "قراردادی": None,  # Contractual
            "پروانه_مجاز": None,  # Licensed
            "مصرفی": None,  # Consumed
            "محاسبه_شده": None,  # Calculated
            "کاهش_یافته": None,  # Reduced
            "تجاوز_از_قدرت": None  # Excess Power
        }
        
        # Pattern matching for each field
        # Handle patterns like "قراردادی محاسبه شده 4525 0" where:
        # - قراردادی = first number (4525)
        # - محاسبه شده = second number (0) or same as قراردادی
        patterns = {
            "قراردادی": [
                r"قراردادی(?!\s+محاسبه)[^\d]*(\d+(?:\.\d+)?)",  # قراردادی not followed by محاسبه
                r"قراردادی\s+محاسبه\s+شده\s+(\d+(?:\.\d+)?)",  # قراردادی محاسبه شده <number>
            ],
            "محاسبه_شده": [
                r"محاسبه\s+شده(?!\s+قراردادی)[^\d]*(\d+(?:\.\d+)?)",  # محاسبه شده standalone
                r"قراردادی\s+محاسبه\s+شده\s+\d+(?:\s+\d+)?\s+(\d+(?:\.\d+)?)",  # Second number after قراردادی محاسبه شده
            ],
            "پروانه_مجاز": [
                r"پروانه\s+مجاز(?!\s+کاهش)[^\d]*(\d+(?:\.\d+)?)",  # پروانه مجاز not followed by کاهش
                r"پروانه\s+مجاز\s+کاهش\s+یافته\s+(\d+(?:\.\d+)?)",  # پروانه مجاز کاهش یافته <number>
            ],
            "کاهش_یافته": [
                r"کاهش\s+یافته(?!\s+پروانه)[^\d]*(\d+(?:\.\d+)?)",  # کاهش یافته standalone
                r"پروانه\s+مجاز\s+کاهش\s+یافته\s+(\d+(?:\.\d+)?)",  # Same as پروانه_مجاز in this case
            ],
            "مصرفی": [
                r"مصرفی\s+\.(\d+(?:\.\d+)?)",  # مصرفی .2470
                r"مصرفی[^\d]*(\d+(?:\.\d+)?)",  # مصرفی followed by number
            ],
            "تجاوز_از_قدرت": [
                r"تجاوز\s+از\s+قدرت[^\d]*(\d+(?:\.\d+)?)"
            ]
        }
        
        # Extract values using patterns
        # Special handling for lines with multiple labels like "قراردادی محاسبه شده 4525 0"
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Handle "قراردادی محاسبه شده 4525 0" pattern
            if "قراردادی" in line and "محاسبه شده" in line:
                numbers = re.findall(r'(\d+(?:\.\d+)?)', line)
                if len(numbers) >= 1:
                    result["قراردادی"] = parse_decimal_number(numbers[0])
                if len(numbers) >= 2:
                    # Second number could be محاسبه شده, but if it's 0, use first number
                    second_val = parse_decimal_number(numbers[1])
                    if second_val and second_val != 0:
                        result["محاسبه_شده"] = second_val
                    else:
                        # If second is 0, محاسبه شده might be same as قراردادی
                        result["محاسبه_شده"] = result["قراردادی"]
            
            # Handle "پروانه مجاز کاهش یافته 3000.0" pattern
            elif "پروانه مجاز" in line and "کاهش یافته" in line:
                numbers = re.findall(r'(\d+(?:\.\d+)?)', line)
                if len(numbers) >= 1:
                    val = parse_decimal_number(numbers[0])
                    result["پروانه_مجاز"] = val
                    result["کاهش_یافته"] = val  # Same value
            
            # Handle other patterns
            else:
                for field, field_patterns in patterns.items():
                    if result[field] is None:  # Only extract if not already found
                        for pattern in field_patterns:
                            match = re.search(pattern, line)
                            if match:
                                value_str = match.group(1)
                                parsed = parse_decimal_number(value_str)
                                if parsed is not None:
                                    result[field] = parsed
                                    break
        
        # Fallback: if some values weren't found, try to extract numbers near labels
        # This handles cases where format is slightly different
        full_text = ' '.join(lines)
        
        # Extract قراردادی if not found
        if result["قراردادی"] is None:
            # Look for "قراردادی" followed by a number
            match = re.search(r'قراردادی[^\d]*(\d+(?:\.\d+)?)', full_text)
            if match:
                result["قراردادی"] = parse_decimal_number(match.group(1))
        
        # Extract پروانه مجاز if not found
        if result["پروانه_مجاز"] is None:
            match = re.search(r'پروانه\s+مجاز[^\d]*(\d+(?:\.\d+)?)', full_text)
            if match:
                result["پروانه_مجاز"] = parse_decimal_number(match.group(1))
        
        # Extract مصرفی if not found (might be written as .2470)
        if result["مصرفی"] is None:
            match = re.search(r'مصرفی[^\d]*\.?(\d+(?:\.\d+)?)', full_text)
            if match:
                result["مصرفی"] = parse_decimal_number(match.group(1))
        
        # Extract محاسبه شده if not found
        if result["محاسبه_شده"] is None:
            match = re.search(r'محاسبه\s+شده[^\d]*(\d+(?:\.\d+)?)', full_text)
            if match:
                result["محاسبه_شده"] = parse_decimal_number(match.group(1))
        
        # Extract کاهش یافته if not found
        if result["کاهش_یافته"] is None:
            match = re.search(r'کاهش\s+یافته[^\d]*(\d+(?:\.\d+)?)', full_text)
            if match:
                result["کاهش_یافته"] = parse_decimal_number(match.group(1))
        
        # Extract تجاوز از قدرت if not found
        if result["تجاوز_از_قدرت"] is None:
            match = re.search(r'تجاوز\s+از\s+قدرت[^\d]*(\d+(?:\.\d+)?)', full_text)
            if match:
                result["تجاوز_از_قدرت"] = parse_decimal_number(match.group(1))
        
        # Create output structure
        extracted_data = {
            "جزئیات_قدرت": result
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(extracted_data, f, ensure_ascii=False, indent=2)
            
        print(f"  - Saved to {output_path}")
        # Print extraction summary (using ASCII-safe format to avoid encoding issues)
        extracted_count = sum(1 for v in result.values() if v is not None)
        print(f"  - Extracted {extracted_count} power values")
        return extracted_data

    except Exception as e:
        print(f"Error restructuring Power Section T4: {e}")
        import traceback
        traceback.print_exc()
        return None
