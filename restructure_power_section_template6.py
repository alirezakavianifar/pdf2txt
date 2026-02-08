"""Restructure power section for Template 6."""
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


def clean_text_artifacts(text):
    """Clean text artifacts like 'امور' and other OCR noise while preserving decimals."""
    if not text:
        return text
    
    # Handle cases like "0.امور 2953" -> "0.2953" by removing artifact between numbers
    # Pattern: digit + dot + artifact + space + digits -> digit + dot + digits
    cleaned = re.sub(r'(\d+\.)امور\s+(\d+)', r'\1\2', text)
    
    # Remove common OCR artifacts
    artifacts = ['امور', 'روما', 'کد اقتصادی :', 'توزیع برق اهو', 'واحد حوادث :', 'علیرضا چراغی']
    for artifact in artifacts:
        cleaned = cleaned.replace(artifact, '')
    
    return cleaned


def parse_decimal_number(text):
    """Parse a number string, removing commas and handling Persian format."""
    if not text:
        return None
    # Clean artifacts first
    clean = clean_text_artifacts(text)
    # Remove commas and spaces
    clean = convert_persian_digits(clean)
    clean = clean.replace(',', '').replace(' ', '').strip()
    try:
        return float(clean)
    except ValueError:
        return None


def extract_all_numbers_from_text(text):
    """Extract all numbers from text, handling various formats and concatenated numbers."""
    # Clean artifacts first
    cleaned_text = clean_text_artifacts(text)
    normalized_text = convert_persian_digits(cleaned_text)
    
    # Handle concatenated numbers like "7 20" -> "720"
    # After cleaning "7امور 20" becomes "7 20", so we concatenate single digit + 2 digits
    # Pattern: single digit, space(s), exactly 2 digits -> concatenate (e.g., "7 20" -> "720")
    concatenated = re.sub(r'(?<!\d)(\d)\s+(\d{2})(?!\d)', r'\1\2', normalized_text)
    
    # Find all numbers (with optional commas and decimals)
    pattern = r'\d+(?:,\d+)*(?:\.\d+)?'
    matches = re.findall(pattern, concatenated)
    numbers = []
    for match in matches:
        parsed = parse_decimal_number(match)
        if parsed is not None:
            numbers.append(parsed)
    return numbers


def extract_power_data(text):
    """Extract power values from text.
    
    Expected fields:
    - قراردادی (Contractual): 2,500
    - قدرت مجاز (Permitted Power): 2,500
    - قدرت قرائت (Read Power): 1,766
    - قدرت فراتش (Exceeded Power): 1,766
    - محاسبه شده (Calculated): 1,766
    - تجاوز از قدرت (Power Exceeded): 2,250
    """
    normalized_text = convert_persian_digits(text)
    
    result = {
        "قراردادی": None,
        "قدرت مجاز": None,
        "قدرت قرائت": None,
        "قدرت فراتش": None,
        "محاسبه شده": None,
        "تجاوز از قدرت": None
    }
    
    lines = normalized_text.split('\n')
    full_text = ' '.join(lines)
    
    # Try reversed text in case Persian text is garbled/reversed
    reversed_text = full_text[::-1]
    
    # More flexible patterns that handle RTL text issues and garbled text
    # Try exact matches first
    patterns = {
        "قراردادی": [
            r'قراردادی[^\d]*(\d+(?:,\d+)?(?:\.\d+)?)',
            r'قراردادي[^\d]*(\d+(?:,\d+)?(?:\.\d+)?)',  # Alternative spelling
        ],
        "قدرت مجاز": [
            r'قدرت\s+مجاز[^\d]*(\d+(?:,\d+)?(?:\.\d+)?)',
            r'قدرت\s*مجاز[^\d]*(\d+(?:,\d+)?(?:\.\d+)?)',
        ],
        "قدرت قرائت": [
            r'قدرت\s+قرائت[^\d]*(\d+(?:,\d+)?(?:\.\d+)?)',
            r'قدرت\s*قرائت[^\d]*(\d+(?:,\d+)?(?:\.\d+)?)',
        ],
        "قدرت فراتش": [
            r'قدرت\s+فراتش[^\d]*(\d+(?:,\d+)?(?:\.\d+)?)',
            r'قدرت\s*فراتش[^\d]*(\d+(?:,\d+)?(?:\.\d+)?)',
        ],
        "محاسبه شده": [
            r'محاسبه\s+شده[^\d]*(\d+(?:,\d+)?(?:\.\d+)?)',
            r'محاسبه\s*شده[^\d]*(\d+(?:,\d+)?(?:\.\d+)?)',
        ],
        "تجاوز از قدرت": [
            r'تجاوز\s+از\s+قدرت[^\d]*(\d+(?:,\d+)?(?:\.\d+)?)',
            r'تجاوز\s*از\s*قدرت[^\d]*(\d+(?:,\d+)?(?:\.\d+)?)',
        ],
    }
    
    # Try each pattern for each field in both normal and reversed text
    for field, field_patterns in patterns.items():
        for pattern in field_patterns:
            # Try normal text
            match = re.search(pattern, full_text)
            if match:
                parsed = parse_decimal_number(match.group(1))
                if parsed is not None:
                    result[field] = parsed
                    break  # Found a match, move to next field
            # Try reversed text
            match = re.search(pattern, reversed_text)
            if match:
                parsed = parse_decimal_number(match.group(1))
                if parsed is not None:
                    result[field] = parsed
                    break  # Found a match, move to next field
    
    # Debug: Print extracted text if no values found
    if all(v is None for v in result.values()):
        # Extract numbers for debugging without printing Persian text
        numbers = extract_all_numbers_from_text(text)
        if numbers:
            print(f"  Warning: No power values extracted from text, but found {len(numbers)} numbers")
        else:
            print(f"  Warning: No power values or numbers found in text")
    
    return result


def extract_power_data_from_geometry(geometry_data):
    """Extract power data from geometry cells."""
    result = {
        "قراردادی": None,
        "قدرت مجاز": None,
        "قدرت قرائت": None,
        "قدرت فراتش": None,
        "محاسبه شده": None,
        "تجاوز از قدرت": None
    }
    
    if not geometry_data or 'cells' not in geometry_data:
        return result
    
    # Collect all text from geometry cells
    cell_texts = []
    for cell in geometry_data['cells']:
        if cell.get('text'):
            cell_texts.append(cell['text'])
    
    # Join all cell texts and extract.
    # Only trust geometry if it looks like it actually contains power labels;
    # otherwise geometry often reflects an unrelated table on the page.
    combined_text = ' '.join(cell_texts)
    if any(k in combined_text for k in ["قراردادی", "قدرت", "محاسبه", "تجاوز"]):
        return extract_power_data(combined_text)
    return result


def restructure_power_section_template6_json(json_path: Path, output_path: Path):
    """Restructure extracted JSON to include power section data for Template 6."""
    print(f"Restructuring Power Section (Template 6) from {json_path}...")
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        text = data.get('text', '')
        table_data = data.get('table', {})
        geometry_data = data.get('geometry', {})
        
        # Also check table rows for power section data
        if table_data and 'rows' in table_data:
            for row in table_data['rows']:
                for cell in row:
                    if cell and isinstance(cell, str):
                        text += '\n' + cell
        
        # Extract power data from text first
        power_data = extract_power_data(text)
        
        # If geometry data is available, try extracting from geometry cells
        # This often has better quality text than the raw text extraction
        if geometry_data and geometry_data.get('cells'):
            geometry_power_data = extract_power_data_from_geometry(geometry_data)
            # Merge: use geometry extraction for any fields that are None in text extraction
            for key in power_data:
                if power_data[key] is None and geometry_power_data.get(key) is not None:
                    power_data[key] = geometry_power_data[key]
        
        # Fallback: If no values extracted and we have numbers in text, try to extract them
        # This handles cases where labels are garbled but numbers are present
        if all(v is None for v in power_data.values()):
            numbers = extract_all_numbers_from_text(text)
            if numbers:
                print(f"  Found {len(numbers)} numbers in text (labels may be garbled): {numbers[:5]}...")
                
                # Separate numbers into categories:
                # - Power values: typically 100-100000 (e.g., 720, 1500, 2500)
                # - Small integers: likely row numbers or counts (< 100)
                # - Decimals < 10: likely coefficients (e.g., 0.2653, 2.081)
                # - Very large numbers: likely not power values
                
                power_values = []
                for n in numbers:
                    # Filter out small integers (row numbers, counts, single digits)
                    if n < 10:
                        continue
                    # Filter out decimals < 10 (coefficients like 0.2653, 2.081)
                    if n < 10 and n != int(n):
                        continue
                    # Filter out date-like numbers (1300-1500 range - Persian calendar years/dates)
                    if 1300 <= n < 1500:
                        continue
                    # Filter out very large numbers (> 100000)
                    if n > 100000:
                        continue
                    # Filter out numbers that look like coefficients (decimals between 10-100)
                    if 10 <= n < 100 and n != int(n) and abs(n - int(n)) > 0.01:
                        continue
                    # Filter out incorrectly concatenated numbers (> 5000 but not common power values)
                    # Common power values: 720, 1500, 2500, 3000, etc. - typically round numbers
                    # Incorrectly concatenated: 7648 (from "7" + "648")
                    if n > 5000 and n % 100 != 0 and n % 10 != 0:
                        # Likely a concatenation error if not a round number
                        continue
                    # Keep numbers in power range: 10-100000 (includes 720, 648, 1500, etc.)
                    power_values.append(n)
                
                if power_values:
                    # Assign to fields in order (this is a heuristic fallback)
                    field_order = ["قراردادی", "قدرت مجاز", "قدرت قرائت", "قدرت فراتش", "محاسبه شده", "تجاوز از قدرت"]
                    for i, field in enumerate(field_order):
                        if i < len(power_values) and power_data[field] is None:
                            power_data[field] = power_values[i]
                            # Use ASCII-safe field name for print
                            field_ascii = field.encode('ascii', 'ignore').decode('ascii') or 'field'
                            print(f"  Assigned {power_values[i]} to {field_ascii} (heuristic)")
                else:
                    print(f"  Warning: Found numbers but none in expected power range (100-100000)")
                    print(f"  All numbers found: {numbers}")
        
        # Build restructured data
        result = {
            "جزئیات قدرت": power_data
        }
        
        # Save restructured JSON
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"  - Saved to {output_path}")
        extracted_count = sum(1 for v in power_data.values() if v is not None)
        print(f"  - Extracted {extracted_count}/{len(power_data)} power values")
        
        return result
        
    except Exception as e:
        print(f"Error restructuring Power Section T6: {e}")
        import traceback
        traceback.print_exc()
        return None

