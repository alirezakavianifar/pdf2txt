
from pathlib import Path
import json
import re
from text_normalization import default_normalizer

def restructure_bill_identifier_template4_json(json_path: Path, output_path: Path):
    """
    Restructures Bill Identifier (Template 4).
    """
    print(f"Restructuring Bill ID (Template 4) from {json_path}...")
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        text = default_normalizer.normalize(data.get("text", ""))
        
        match = re.search(r"\d{13}", text)
        bill_id = match.group(0) if match else None
        
        result = {"bill_identifier": bill_id}
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
            
        return result
    except Exception as e:
        print(f"Error restructuring Bill ID T4: {e}")
        return None
