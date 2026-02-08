
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

def extract_from_geometry(geometry_data, result):
    """
    Extract power values from geometry cells by finding labels and their adjacent values.
    The table structure has labels in one column and values in adjacent columns.
    """
    if not geometry_data or 'cells' not in geometry_data:
        return
    
    cells = geometry_data['cells']
    if not cells:
        return
    
    # Build a matrix of cells by row and column
    max_row = max(c.get('row', 0) for c in cells)
    max_col = max(c.get('col', 0) for c in cells)
    
    # Create a 2D grid to store cell text
    grid = {}
    for cell in cells:
        row = cell.get('row', 0)
        col = cell.get('col', 0)
        text = cell.get('text', '').strip()
        if text:
            grid[(row, col)] = text
    
    # Power field mappings
    field_mappings = {
        'قراردادی': 'قراردادی',
        'پروانه_مجاز': 'پروانه مجاز',
        'مصرفی': 'مصرفی',
        'محاسبه_شده': 'محاسبه شده',
        'کاهش_یافته': 'کاهش یافته',
        'تجاوز_از_قدرت': 'تجاوز از قدرت'
    }
    
    # Find cells containing power labels and extract values from adjacent cells
    for row in range(max_row + 1):
        for col in range(max_col + 1):
            cell_text = grid.get((row, col), '')
            if not cell_text:
                continue
            
            # Normalize cell text for matching (apply BIDI to handle reversed text)
            normalized_cell = default_normalizer.normalize(cell_text, apply_bidi=True)
            
            # Check each power field
            for result_key, label in field_mappings.items():
                if result[result_key] is not None:
                    continue  # Already found
                
                # Check if this cell contains the label
                if label in normalized_cell:
                    # First, try to extract value from the same cell (label and value together)
                    # Find the position of the label in the cell
                    label_pos = normalized_cell.find(label)
                    if label_pos >= 0:
                        # Look for numbers after the label in the same cell
                        # Extract text after the label (up to next label or end)
                        text_after_label = normalized_cell[label_pos + len(label):]
                        # Find the next label to limit the search
                        next_label_pos = len(text_after_label)
                        for other_label in field_mappings.values():
                            if other_label != label:
                                pos = text_after_label.find(other_label)
                                if pos >= 0 and pos < next_label_pos:
                                    next_label_pos = pos
                        
                        # Search for numbers in the text segment after this label
                        search_text = text_after_label[:next_label_pos]
                        numbers_after = re.findall(r'[\d۰-۹]+(?:[\./][\d۰-۹]+)?', search_text)
                        if numbers_after:
                            # Take the first number after the label
                            normalized_num = default_normalizer.normalize(numbers_after[0], apply_bidi=False)
                            parsed = parse_decimal_number(normalized_num)
                            if parsed is not None and parsed >= 0:  # Allow 0 values
                                result[result_key] = parsed
                                continue  # Found in same cell, move to next field
                    
                    # If not found in same cell, look for numeric value in adjacent cells
                    # Try columns to the right first (typical table layout: label | value)
                    for offset in range(1, min(5, max_col - col + 1)):
                        adjacent_text = grid.get((row, col + offset), '')
                        if adjacent_text:
                            # Normalize the adjacent cell text (apply BIDI to handle reversed text)
                            normalized_adjacent = default_normalizer.normalize(adjacent_text, apply_bidi=True)
                            # Check if it contains a number (Persian or English digits)
                            numbers = re.findall(r'[\d۰-۹]+(?:[\./][\d۰-۹]+)?', normalized_adjacent)
                            if numbers:
                                # Convert Persian digits and parse
                                normalized_num = default_normalizer.normalize(numbers[0], apply_bidi=False)
                                parsed = parse_decimal_number(normalized_num)
                                if parsed is not None and parsed >= 0:  # Allow 0 values
                                    result[result_key] = parsed
                                    break
                    
                    # Also try cells to the left (in case table is reversed)
                    if result[result_key] is None and col > 0:
                        for offset in range(1, min(5, col + 1)):
                            adjacent_text = grid.get((row, col - offset), '')
                            if adjacent_text:
                                normalized_adjacent = default_normalizer.normalize(adjacent_text, apply_bidi=True)
                                numbers = re.findall(r'[\d۰-۹]+(?:[\./][\d۰-۹]+)?', normalized_adjacent)
                                if numbers:
                                    normalized_num = default_normalizer.normalize(numbers[0], apply_bidi=False)
                                    parsed = parse_decimal_number(normalized_num)
                                    if parsed is not None and parsed >= 0:  # Allow 0 values
                                        result[result_key] = parsed
                                        break

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
        geometry_data = data.get("geometry", {})
        
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
        
        # Use geometry data to extract values from table structure FIRST
        # This is important for cases where text extraction misses values
        # Geometry extraction can find values in adjacent table cells
        extract_from_geometry(geometry_data, result)
        
        # Fallback: Extract from text if not found in geometry
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
            # Try multiple patterns for مصرفی
            patterns = [
                r'مصرفی[^\d]*\.?(\d+(?:\.\d+)?)',  # مصرفی followed by number
                r'مصرفی\s*[:\-]?\s*(\d+(?:\.\d+)?)',  # مصرفی: number or مصرفی - number
            ]
            for pattern in patterns:
                match = re.search(pattern, full_text)
                if match:
                    result["مصرفی"] = parse_decimal_number(match.group(1))
                    break
        
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
