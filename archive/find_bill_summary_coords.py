"""Find coordinates for bill summary section (بهای انرژی, آبونمان, etc)."""
import fitz
from pathlib import Path

def find_bill_summary_coordinates(pdf_path, output_file):
    """Find bill summary section coordinates and write to file."""
    pdf_path_obj = Path(pdf_path)
    doc = fitz.open(pdf_path)
    page = doc[0]
    
    text_dict = page.get_text("dict")
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("=" * 70 + "\n")
        f.write(f"BILL SUMMARY LOCATIONS IN: {pdf_path_obj.name}\n")
        f.write("=" * 70 + "\n\n")
        
        # Keywords to search for
        keywords = ["بهای انرژی", "بهاي انرژي", "آبونمان", "عوارض برق", "مالیات", "جمع دوره", "بدهکاری", "بدهكاري", "کسر هزار ریال"]
        
        found_items = []
        
        for block_idx, block in enumerate(text_dict.get("blocks", [])):
            if "lines" in block:
                for line in block.get("lines", []):
                    for span in line.get("spans", []):
                        text = span.get("text", "").strip()
                        bbox = span.get("bbox", [])
                        if text and len(bbox) == 4:
                            # Check if text contains any keywords
                            for keyword in keywords:
                                if keyword in text or text in keyword:
                                    found_items.append({
                                        "text": text,
                                        "bbox": bbox,
                                        "keyword": keyword
                                    })
                                    f.write(f"Text: '{text}'\n")
                                    f.write(f"  Keyword match: '{keyword}'\n")
                                    f.write(f"  Position: x0={bbox[0]:.1f}, y0={bbox[1]:.1f}, x1={bbox[2]:.1f}, y1={bbox[3]:.1f}\n")
                                    break
        
        # Suggest crop box
        if found_items:
            # Filter for items that are likely in the same column (bottom left typically)
            # Or just take the bounds of all found items
            
            all_x0 = [item["bbox"][0] for item in found_items]
            all_y0 = [item["bbox"][1] for item in found_items]
            all_x1 = [item["bbox"][2] for item in found_items]
            all_y1 = [item["bbox"][3] for item in found_items]
            
            min_x = min(all_x0)
            min_y = min(all_y0)
            max_x = max(all_x1)
            max_y = max(all_y1)
            
            # The values are likely to the left of the labels (RTL) or right?
            # In the image, values are on the LEFT, labels on the RIGHT.
            # So we need to expand LEFT to include values.
            # Keywords find the LABELS.
            # Example: "بهای انرژی" (Label) x range [500, 550] (Made up)
            # Value "280,255,152" would be at x range [400, 490]
            
            # Let's expand strictly to the left by a safe margin (e.g. 150 points)
            margin_right = 10
            margin_left = 150 
            margin_top = 10
            margin_bottom = 10
            
            x0 = max(0, min_x - margin_left)
            y0 = max(0, min_y - margin_top)
            x1 = min(page.mediabox.width, max_x + margin_right)
            y1 = min(page.mediabox.height, max_y + margin_bottom)
            
            f.write("\n" + "=" * 70 + "\n")
            f.write("SUGGESTED CROP COORDINATES (Labels + Left Values):\n")
            f.write("=" * 70 + "\n")
            f.write(f"x0: {x0:.1f}\n")
            f.write(f"y0: {y0:.1f}\n")
            f.write(f"x1: {x1:.1f}\n")
            f.write(f"y1: {y1:.1f}\n")
            f.write(f"Width: {x1 - x0:.1f}, Height: {y1 - y0:.1f}\n")
    
    doc.close()
    print(f"Results written to: {output_file}")

if __name__ == "__main__":
    sample_pdf = Path("template1/1.pdf")
    output_file = Path("output/bill_summary_coords.txt")
    output_file.parent.mkdir(exist_ok=True)
    
    if sample_pdf.exists():
        find_bill_summary_coordinates(str(sample_pdf), str(output_file))
    else:
        print(f"PDF not found: {sample_pdf}")
