import json
from pathlib import Path
import sys

def search_files(directory, term):
    dir_path = Path(directory)
    output_path = Path("check_field_location_output.txt")
    
    with open(output_path, 'a', encoding='utf-8') as out_f:
        out_f.write(f"Searching for '{term}' in {directory}...\n")
        
        for file_path in dir_path.glob("*.json"):
            if "restructured" in file_path.name:
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                if term in content:
                    out_f.write(f"Found '{term}' in {file_path.name}\n")
                    
                    try:
                        data = json.loads(content)
                        if 'text' in data:
                            start = data['text'].find(term)
                            if start != -1:
                                snippet = data['text'][max(0, start-100):min(len(data['text']), start+200)]
                                out_f.write(f"  Snippet: ...{snippet.replace(chr(10), ' ')}...\n")
                    except Exception as e:
                        out_f.write(f"  Error parsing JSON for context: {e}\n")
                        
            except Exception as e:
                out_f.write(f"Error reading {file_path.name}: {e}\n")

if __name__ == "__main__":
    search_term1 = "ماده ۱۶"
    search_term2 = "جهش تولید"
    directory = "output/4_510_9019722204129"
    
    # Clear output file first
    with open("check_field_location_output.txt", 'w', encoding='utf-8') as f:
        pass
        
    search_files(directory, search_term1)
    search_files(directory, search_term2)
