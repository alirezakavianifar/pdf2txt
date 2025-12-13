"""Find text location in PDF to determine crop coordinates."""
import fitz
from pathlib import Path

def find_all_text_locations(pdf_path, output_file):
    """Find all text locations in PDF and write to file."""
    pdf_path_obj = Path(pdf_path)
    doc = fitz.open(pdf_path)
    page = doc[0]
    
    text_dict = page.get_text("dict")
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("=" * 70 + "\n")
        f.write(f"TEXT LOCATIONS IN: {pdf_path_obj.name}\n")
        f.write("=" * 70 + "\n\n")
        
        for block_idx, block in enumerate(text_dict.get("blocks", [])):
            if "lines" in block:
                for line in block.get("lines", []):
                    for span in line.get("spans", []):
                        text = span.get("text", "").strip()
                        bbox = span.get("bbox", [])
                        if text and len(bbox) == 4:
                            f.write(f"Text: '{text}'\n")
                            f.write(f"  Position: x0={bbox[0]:.1f}, y0={bbox[1]:.1f}, x1={bbox[2]:.1f}, y1={bbox[3]:.1f}\n")
                            f.write(f"  Width: {bbox[2] - bbox[0]:.1f}, Height: {bbox[3] - bbox[1]:.1f}\n\n")
                            
                            # Check if this might be the license expiry section
                            if "انقضا" in text or "پروانه" in text or "تاریخ" in text:
                                f.write("  *** POSSIBLE LICENSE EXPIRY SECTION ***\n")
                                margin = 10
                                x0 = max(0, bbox[0] - margin)
                                y0 = max(0, bbox[1] - margin)
                                x1 = min(page.mediabox.width, bbox[2] + margin)
                                y1 = min(page.mediabox.height, bbox[3] + margin * 2)
                                f.write(f"  Suggested crop: x0={x0:.1f}, y0={y0:.1f}, x1={x1:.1f}, y1={y1:.1f}\n\n")
    
    doc.close()
    print(f"Results written to: {output_file}")

if __name__ == "__main__":
    sample_pdf = Path("template1/1.pdf")
    output_file = Path("output/text_locations_1.txt")
    
    if sample_pdf.exists():
        find_all_text_locations(str(sample_pdf), str(output_file))
    else:
        print(f"PDF not found: {sample_pdf}")
