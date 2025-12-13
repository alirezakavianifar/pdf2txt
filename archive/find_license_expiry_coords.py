"""Interactive script to find coordinates for license expiry section."""
import fitz
from pathlib import Path

def find_text_coordinates(pdf_path, search_text, output_file=None):
    """Find coordinates of text in PDF."""
    doc = fitz.open(pdf_path)
    page = doc[0]
    
    def log(msg):
        if output_file:
            output_file.write(msg + "\n")
        else:
            print(msg)
    
    # Search for the text
    text_instances = page.search_for(search_text)
    
    if text_instances:
        # Get the first instance
        rect = text_instances[0]
        log(f"Found '{search_text}' at:")
        log(f"  x0: {rect.x0:.1f}, y0: {rect.y0:.1f}")
        log(f"  x1: {rect.x1:.1f}, y1: {rect.y1:.1f}")
        log(f"  Width: {rect.width:.1f}, Height: {rect.height:.1f}")
        
        # Suggest crop box (expand a bit around the text)
        margin = 10
        x0 = max(0, rect.x0 - margin)
        y0 = max(0, rect.y0 - margin)
        x1 = min(page.mediabox.width, rect.x1 + margin)
        y1 = min(page.mediabox.height, rect.y1 + margin * 2)  # More space below
        
        log(f"\nSuggested crop coordinates:")
        log(f"  x0: {x0:.1f}, y0: {y0:.1f}, x1: {x1:.1f}, y1: {y1:.1f}")
        
        doc.close()
        return (x0, y0, x1, y1)
    else:
        # Try searching for partial text
        text_dict = page.get_text("dict")
        for text_item in text_dict.get("blocks", []):
            if "lines" in text_item:
                for line in text_item["lines"]:
                    for span in line["spans"]:
                        span_text = span.get("text", "")
                        if search_text in span_text:
                            bbox = span["bbox"]
                            log(f"Found partial match at:")
                            log(f"  x0: {bbox[0]:.1f}, y0: {bbox[1]:.1f}")
                            log(f"  x1: {bbox[2]:.1f}, y1: {bbox[3]:.1f}")
                            margin = 10
                            x0 = max(0, bbox[0] - margin)
                            y0 = max(0, bbox[1] - margin)
                            x1 = min(page.mediabox.width, bbox[2] + margin)
                            y1 = min(page.mediabox.height, bbox[3] + margin * 2)
                            log(f"\nSuggested crop coordinates:")
                            log(f"  x0: {x0:.1f}, y0: {y0:.1f}, x1: {x1:.1f}, y1: {y1:.1f}")
                            doc.close()
                            return (x0, y0, x1, y1)
        log(f"Text '{search_text}' not found in PDF")
        doc.close()
        return None

if __name__ == "__main__":
    # Try to find coordinates for license expiry section
    # The text should be: "تاریخ انقضا پروانه" or similar
    sample_pdf = Path("template1/1.pdf")
    
    if not sample_pdf.exists():
        print(f"Sample PDF not found: {sample_pdf}")
        exit(1)
    
    with open("output/license_expiry_coords.txt", "w", encoding="utf-8") as f:
        f.write("=" * 70 + "\n")
        f.write("FINDING LICENSE EXPIRY SECTION COORDINATES\n")
        f.write("=" * 70 + "\n")
        
        # Try different search texts
        search_texts = [
            "تاریخ انقضا پروانه",
            "تاریخ انقضا",
            "پروانه",
            "انقضا"
        ]
        
        coords = None
        for search_text in search_texts:
            f.write(f"\nSearching for: '{search_text}'\n")
            coords = find_text_coordinates(str(sample_pdf), search_text, f)
            if coords:
                f.write(f"\n✓ Found coordinates using: '{search_text}'\n")
                break
        
        if coords:
            f.write("\n" + "=" * 70 + "\n")
            f.write("COORDINATES TO USE IN adjust_crop.py:\n")
            f.write("=" * 70 + "\n")
            f.write(f'x0: {coords[0]:.1f}\n')
            f.write(f'y0: {coords[1]:.1f}\n')
            f.write(f'x1: {coords[2]:.1f}\n')
            f.write(f'y1: {coords[3]:.1f}\n')
        else:
            f.write("\nCould not automatically find coordinates.\n")
            f.write("Please check the PDF manually and provide coordinates.\n")
    
    print("Results written to output/license_expiry_coords.txt")
