import json
import sys

def debug_unicode(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    text = data.get('text', '')
    print(f"--- Text for {filename} ---")
    print(json.dumps(text, ensure_ascii=True))

if __name__ == "__main__":
    files = [
        "output/1_bill_summary_section.json",
        "output/4_510_9019722204129_bill_summary_section.json"
    ]
    for f in files:
        try:
            debug_unicode(f)
        except Exception as e:
            print(f"Error {f}: {e}")
