"""Find coordinates for power section (قدرت کیلووات)."""
import fitz
from pathlib import Path

def find_power_section_coordinates(pdf_path, output_file):
    """Find power section coordinates and write to file."""
    pdf_path_obj = Path(pdf_path)
    doc = fitz.open(pdf_path)
    page = doc[0]
    
    text_dict = page.get_text("dict")
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("=" * 70 + "\n")
        f.write(f"POWER SECTION LOCATIONS IN: {pdf_path_obj.name}\n")
        f.write("=" * 70 + "\n\n")
        
        # Keywords to search for
        keywords = ["قدرت", "کیلووات", "قراردادی", "محاسبه شده", "مصرفی", "ماکسیمتر", "تجاوز"]
        
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
                                if keyword in text:
                                    found_items.append({
                                        "text": text,
                                        "bbox": bbox,
                                        "keyword": keyword
                                    })
                                    f.write(f"Text: '{text}'\n")
                                    f.write(f"  Keyword match: '{keyword}'\n")
                                    f.write(f"  Position: x0={bbox[0]:.1f}, y0={bbox[1]:.1f}, x1={bbox[2]:.1f}, y1={bbox[3]:.1f}\n")
                                    f.write(f"  Width: {bbox[2] - bbox[0]:.1f}, Height: {bbox[3] - bbox[1]:.1f}\n\n")
                                    break
        
        # If we found items, suggest a crop box
        if found_items:
            all_x0 = [item["bbox"][0] for item in found_items]
            all_y0 = [item["bbox"][1] for item in found_items]
            all_x1 = [item["bbox"][2] for item in found_items]
            all_y1 = [item["bbox"][3] for item in found_items]
            
            min_x = min(all_x0)
            min_y = min(all_y0)
            max_x = max(all_x1)
            max_y = max(all_y1)
            
            margin = 10
            x0 = max(0, min_x - margin)
            y0 = max(0, min_y - margin)
            x1 = min(page.mediabox.width, max_x + margin)
            y1 = min(page.mediabox.height, max_y + margin * 2)
            
            f.write("\n" + "=" * 70 + "\n")
            f.write("SUGGESTED CROP COORDINATES:\n")
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
    output_file = Path("output/power_section_coords.txt")
    
    if sample_pdf.exists():
        find_power_section_coordinates(str(sample_pdf), str(output_file))
    else:
        print(f"PDF not found: {sample_pdf}")
