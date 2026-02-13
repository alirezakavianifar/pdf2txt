import json
import re
import sys
from pathlib import Path
from text_normalization import default_normalizer

def test_debug(json_path):
    if not Path(json_path).exists():
        print(f"File {json_path} not found.")
        return
        
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    text_sources = []
    if data.get("text"):
        text_sources.append(data.get("text"))
    
    table = data.get("table", {})
    rows = table.get("rows", [[]])
    if isinstance(rows, list):
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
    
    print(f"--- DEBUG FOR {json_path} ---")
    print(f"Normalized Text Snippet: {normalized_text[:500]}")
    
    expiry_keywords = ["انقضا", "اعتبار"]
    matches = list(re.finditer(r"(\d{4}/\d{1,2}/\d{1,2})", normalized_text))
    
    print(f"Total Matches found: {len(matches)}")
    for match in matches:
        date_str = match.group(1)
        start = max(0, match.start() - 30)
        end = min(len(normalized_text), match.end() + 30)
        context = normalized_text[start:end]
        has_kw = any(kw in context for kw in expiry_keywords)
        print(f"  - Date: {date_str}, Has Keyword: {has_kw}, Context: '{context}'")

if __name__ == "__main__":
    # Force utf-8 output for terminal
    if sys.stdout.encoding != 'utf-8':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        
    test_debug("output/2_1000_9893267403225/2_1000_9893267403225_license_expiry_section.json")
    test_debug("output/2_1000_9893267403225/2_1000_9893267403225_bill_identifier_section.json")
