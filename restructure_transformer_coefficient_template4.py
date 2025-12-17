
from pathlib import Path
import json
import re
from text_normalization import default_normalizer

def restructure_transformer_coefficient_template4_json(json_path: Path, output_path: Path):
    """
    Restructures Transformer Coefficient (Template 4).
    Extracts the transformer coefficient value from text like "ضریب ترانس 8000".
    """
    print(f"Restructuring Transformer Coeff (Template 4) from {json_path}...")
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        text = default_normalizer.normalize(data.get("text", ""))
        
        coeff = None
        
        # First, try to find the number directly after "ضریب ترانس" or "ضریب ترانس:"
        # Pattern: "ضریب ترانس" followed by optional colon/space and then a number
        match = re.search(r'ضریب\s*ترانس\s*:?\s*(\d+)', text, re.IGNORECASE)
        if match:
            coeff = int(match.group(1))
        else:
            # Fallback: find all numbers and take the first one with length >= 3
            # (to exclude small numbers like page numbers, dates, etc.)
            nums = re.findall(r"\d+", text)
            for n in nums:
                if len(n) >= 3:  # exclude small numbers
                    coeff = int(n)
                    break
               
        # Use Persian field name to match the pattern used in other template 4 sections
        result = {"ضریب_ترانس": coeff}
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
            
        return result
    except Exception as e:
        print(f"Error restructuring Transformer T4: {e}")
        return None
