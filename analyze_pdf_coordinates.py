
import pdfplumber
import sys

def analyze_pdf(pdf_path, output_file):
    print(f"Analyzing {pdf_path}...")
    try:
        with pdfplumber.open(pdf_path) as pdf:
            page = pdf.pages[0]
            width = page.width
            height = page.height
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"Page Size: {width}x{height}\n")
                
                # Extract words
                words = page.extract_words()
                
                # Group by line (approximate by top coordinate)
                lines = {}
                for word in words:
                    top = round(word['top'], 1)  # Round to nearest decimal for grouping
                    if top not in lines:
                        lines[top] = []
                    lines[top].append(word)
                
                sorted_tops = sorted(lines.keys())
                
                f.write("\n--- Content by Y-Coordinate ---\n")
                for top in sorted_tops:
                    line_words = sorted(lines[top], key=lambda w: w['x0'])
                    # Filter out tiny specks often found in scanned/complex PDFs? 
                    # For now keep all.
                    text = " ".join([w['text'] for w in line_words])
                    x_start = line_words[0]['x0']
                    x_end = line_words[-1]['x1']
                    f.write(f"Y={top:.2f} | X={x_start:.2f}-{x_end:.2f} | Text: {text}\n")
                    
        print(f"Analysis saved to {output_file}")

    except Exception as e:
        print(f"Error analyzing PDF: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python analyze_pdf_coordinates.py <pdf_file> [output_file]")
    else:
        out_file = sys.argv[2] if len(sys.argv) > 2 else "analysis_output.txt"
        analyze_pdf(sys.argv[1], out_file)
