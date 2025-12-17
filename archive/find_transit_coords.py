
import pdfplumber
import sys

# Set stdout to utf-8
sys.stdout.reconfigure(encoding='utf-8')

def find_text_coords(pdf_path, search_terms):
    print(f"Searching in {pdf_path}...", flush=True)
    try:
        with pdfplumber.open(pdf_path) as pdf:
            page = pdf.pages[0]
            words = page.extract_words()
            
            for term in search_terms:
                print(f"\n--- Searching for: {term} ---")
                found_for_term = False
                for w in words:
                    # Check text equality or substring
                    # Handle comma differences
                    text_clean = w['text'].replace(',', '')
                    term_clean = term.replace(',', '')
                    
                    if term_clean in text_clean:
                        print(f"  Found '{w['text']}' at: x0={w['x0']:.2f}, top={w['top']:.2f}, x1={w['x1']:.2f}, bottom={w['bottom']:.2f}")
                        found_for_term = True
                
                if not found_for_term:
                    print(f"  Not found.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Search for numbers seen in the screenshot
    # 509400 (Rate)
    # 170 (Power)
    # 1404/01/01 (Date)
    # 89,484,600 (Transit Cost)
    search_terms = ["509400", "170", "1404/01/01", "89484600"]
    find_text_coords("template1/1.pdf", search_terms)
