"""Find coordinates for consumption history section."""
import fitz
import pdfplumber
from pathlib import Path

def find_consumption_history_coords(pdf_path, output_file):
    """Find coordinates for consumption history section."""
    pdf_path_obj = Path(pdf_path)
    
    # Use pdfplumber to extract text with positions
    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[0]
        
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("=" * 70 + "\n")
            f.write(f"CONSUMPTION HISTORY SECTION LOCATIONS IN: {pdf_path_obj.name}\n")
            f.write("=" * 70 + "\n\n")
            
            # Extract all words with their positions
            words = page.extract_words()
            
            # Look for date patterns (YYYY/MM/DD) that might be in the table
            date_patterns = []
            found_y_positions = []
            
            for word in words:
                text = word.get('text', '')
                # Check for date-like patterns (4 digits / 2 digits / 2 digits)
                if '/' in text and len(text) >= 8:
                    try:
                        parts = text.split('/')
                        if len(parts) == 3:
                            if len(parts[0]) >= 3 and parts[1].isdigit() and parts[2].isdigit():
                                date_patterns.append((text, word))
                                found_y_positions.append(word.get('top', 0))
                                f.write(f"Found date-like pattern: '{text}'\n")
                                f.write(f"  Position: x0={word.get('x0', 0):.1f}, y0={word.get('top', 0):.1f}, x1={word.get('x1', 0):.1f}, y1={word.get('bottom', 0):.1f}\n\n")
                    except:
                        pass
            
            # Look for large numbers (amounts like 4345169.9)
            for word in words:
                text = word.get('text', '').replace(',', '')
                try:
                    num = float(text)
                    if num > 1000000:  # Large amounts
                        f.write(f"Found large number (possible amount): '{text}' = {num}\n")
                        f.write(f"  Position: x0={word.get('x0', 0):.1f}, y0={word.get('top', 0):.1f}, x1={word.get('x1', 0):.1f}, y1={word.get('bottom', 0):.1f}\n\n")
                        found_y_positions.append(word.get('top', 0))
                except:
                    pass
            
            # Suggest coordinates based on found patterns
            if found_y_positions:
                # Find the range where dates/amounts appear
                min_y = min(found_y_positions)
                max_y = max(found_y_positions)
                
                # Add some margin and estimate table boundaries
                margin = 10
                y0 = max(0, min_y - margin * 2)  # Start a bit higher to include headers
                y1 = min(page.height, max_y + margin * 2)  # End a bit lower
                x0 = 5  # Start from left edge
                x1 = page.width - 5  # End at right edge
                
                f.write("\n" + "=" * 70 + "\n")
                f.write("SUGGESTED CROP COORDINATES:\n")
                f.write("=" * 70 + "\n")
                f.write(f"x0={x0:.1f}, y0={y0:.1f}, x1={x1:.1f}, y1={y1:.1f}\n")
                f.write(f"Size: {x1-x0:.1f} x {y1-y0:.1f} points\n")
            else:
                # Fallback: estimate based on period section position
                # Period section ends at y=285, so this table likely starts around y=290-300
                f.write("\nNo dates/amounts found. Using estimated coordinates:\n")
                f.write("(Based on period_section ending at y=285)\n")
                y0 = 290
                y1 = 450  # Estimated height for 6-7 rows
                x0 = 5
                x1 = page.width - 5
                f.write(f"Estimated: x0={x0:.1f}, y0={y0:.1f}, x1={x1:.1f}, y1={y1:.1f}\n")
    
    print(f"Results written to: {output_file}")

if __name__ == "__main__":
    sample_pdf = Path("template1/1.pdf")
    output_file = Path("output/consumption_history_coords.txt")
    
    output_file.parent.mkdir(exist_ok=True)
    
    if sample_pdf.exists():
        find_consumption_history_coords(str(sample_pdf), str(output_file))
    else:
        print(f"PDF not found: {sample_pdf}")

