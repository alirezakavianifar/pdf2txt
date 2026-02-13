
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
        
        # Gather all possible text
        text_sources = []
        if data.get("text"):
            text_sources.append(data.get("text"))
        
        table = data.get("table", {})
        rows = table.get("rows", [])
        for row in rows:
            if row:
                text_sources.append(" ".join([str(cell) for cell in row if cell]))
        
        geometry = data.get("geometry", {})
        cells = geometry.get("cells", [])
        for cell in cells:
            if cell.get("text"):
                text_sources.append(cell.get("text"))
        
        combined_text = " ".join(text_sources)
        normalized_text = default_normalizer.normalize(combined_text)
        
        # Look for date pattern YYYY/MM/DD with expiry keywords nearby
        expiry_keywords = ["انقضا", "اعتبار"]
        
        # Try to find dates near keywords first
        matches = re.finditer(r"(\d{4}/\d{1,2}/\d{1,2})", normalized_text)
        expiry_date = None
        
        for match in matches:
            date_str = match.group(1)
            # Check context around the match (e.g., 20 chars before and after)
            start = max(0, match.start() - 30)
            end = min(len(normalized_text), match.end() + 30)
            context = normalized_text[start:end]
            
            if any(kw in context for kw in expiry_keywords):
                expiry_date = date_str
                break
        
        # Fallback to the first date starting with 14 or 15 if no keyword match
        if not expiry_date:
            matches = re.findall(r"(\d{4}/\d{1,2}/\d{1,2})", normalized_text)
            for date_str in matches:
                if date_str.startswith("14") or date_str.startswith("15"):
                    expiry_date = date_str
                    break
            
        result = {"license_expiry_date": expiry_date}
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
            
        return result
    except Exception as e:
        print(f"Error restructuring License Expiry T4: {e}")
        return None
