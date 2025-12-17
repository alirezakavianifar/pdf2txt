
from pathlib import Path
import json
import re
from text_normalization import default_normalizer

def restructure_license_expiry_template4_json(json_path: Path, output_path: Path):
    """
    Restructures License Expiry Section (Template 4).
    """
    print(f"Restructuring License Expiry (Template 4) from {json_path}...")
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        text = default_normalizer.normalize(data.get("text", ""))
        
        # Look for date pattern YYYY/MM/DD
        match = re.search(r"\d{4}/\d{2}/\d{2}", text)
        expiry_date = match.group(0) if match else None
        
        result = {"license_expiry_date": expiry_date}
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
            
        return result
    except Exception as e:
        print(f"Error restructuring License Expiry T4: {e}")
        return None
