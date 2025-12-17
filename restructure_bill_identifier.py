import json
import re
import sys

def restructure_bill_identifier_json(input_json_path, output_json_path):
    """
    Restructure the bill identifier section.
    """
    try:
        with open(input_json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        raw_text = data.get('text', '')
        
        # Normalize Persian digits just in case (though pipeline does it)
        persian_digits = '۰۱۲۳۴۵۶۷۸۹'
        english_digits = '0123456789'
        translation_table = str.maketrans(persian_digits, english_digits)
        text = raw_text.translate(translation_table)
        
        # Look for 13 digit number
        # It might have spaces or be clean
        # Remove spaces to check
        text_clean = text.replace(' ', '').replace('\n', '')
        
        match = re.search(r'\d{13}', text_clean)
        identifier = match.group(0) if match else None
        
        # If not found, try finding any long number
        if not identifier:
             # Find longest sequence of digits
             matches = re.findall(r'\d+', text_clean)
             if matches:
                 identifier = max(matches, key=len)
        
        result = {
            "شناسه قبض": identifier
        }
        
        with open(output_json_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
            
        return result

    except Exception as e:
        print(f"Error structuring bill identifier: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    if len(sys.argv) > 2:
        restructure_bill_identifier_json(sys.argv[1], sys.argv[2])
