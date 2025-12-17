import pdfplumber

def list_words(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[0]
        words = page.extract_words()
        
        # Sort by y then x
        words.sort(key=lambda w: (w['top'], w['x0']))
        
        for w in words:
            # Print words that might resemble our target
            if "شناسه" in w['text'] or "قبض" in w['text'] or "6009737501320" in w['text']:
                print(w)
            
            # Also print all words in a specific y-range if known, but we don't know yet.
            # Let's just print everything to a file so I can grep it.
            
if __name__ == "__main__":
    list_words("template1/1.pdf")
