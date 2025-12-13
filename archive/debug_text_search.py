"""Dump all text with coordinates to find hidden text."""
import fitz
from pathlib import Path

def dump_all_text(pdf_path, output_file):
    doc = fitz.open(pdf_path)
    page = doc[0]
    
    text_dict = page.get_text("dict")
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(f"ALL TEXT IN: {Path(pdf_path).name}\n")
        f.write("=" * 50 + "\n")
        
        for block in text_dict.get("blocks", []):
            if "lines" in block:
                for line in block.get("lines", []):
                    for span in line.get("spans", []):
                        text = span.get("text", "").strip()
                        if text:
                            # Print regular and reversed (for RTL checks)
                            f.write(f"Text: '{text}' (Rev: '{text[::-1]}')\n")
                            bbox = span["bbox"]
                            f.write(f"  BBox: ({bbox[0]:.1f}, {bbox[1]:.1f}, {bbox[2]:.1f}, {bbox[3]:.1f})\n")
    
    print(f"Dumped to {output_file}")

if __name__ == "__main__":
    dump_all_text("template1/1.pdf", "output/all_text_debug.txt")
