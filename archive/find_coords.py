import pdfplumber
from pathlib import Path

def find_text_coords(pdf_path, search_terms):
    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[0]
        words = page.extract_words()
        
        print(f"Page size: {page.width}x{page.height}")
        
        target_values = [
            "از", "تاریخ", "تا", "مدت",
            "1404/02/01", "1403/12/22", "40"
        ]
        
        # Sort words
        sorted_words = sorted(words, key=lambda w: (int(w['top'] / 10), w['x0']))
        
        print(f"Page size: {page.width}x{page.height}")
        print("-" * 50)
        
        with open('coords_out.txt', 'w', encoding='utf-8') as f:
            for w in sorted_words:
                 if 270 < w['top'] < 300:
                     f.write(f"TEXT: '{w['text']}' x={w['x0']:.0f}-{w['x1']:.0f} y={w['top']:.0f}-{w['bottom']:.0f}\n")

if __name__ == "__main__":
    pdf_path = Path("template_2/2.pdf")
    # Keywords matching the 5 sections
    keywords = [
        "شناسه", "قبض",  # Bill Identifier
        "انقضا", "پروانه", # License Expiry
        "شرح", "مصرف", "میان", "باری", # Energy Supported (Table headers)
        "قدرت", "کیلووات", "قراردادی", # Power Section
        "از", "تاریخ", "تا", "روز" # Period Section
    ]
    if pdf_path.exists():
        find_text_coords(pdf_path, keywords)
    else:
        print(f"{pdf_path} not found")
