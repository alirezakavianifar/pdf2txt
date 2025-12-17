import pdfplumber

def dump_all(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[0]
        words = page.extract_words()
        with open("words_dump.txt", "w", encoding="utf-8") as f:
            for w in words:
                f.write(f"{w['text']} | Box: {w['x0']},{w['top']},{w['x1']},{w['bottom']}\n")

if __name__ == "__main__":
    dump_all("template1/1.pdf")
