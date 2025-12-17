
from adjust_crop import apply_crop_with_coords
from extract_text import PDFTextExtractor
from pathlib import Path
import sys

# Set stdout to utf-8
sys.stdout.reconfigure(encoding='utf-8')

def test_crop_and_extract():
    pdf_path = "template1/1.pdf"
    output_path = "output/debug_transit.pdf"
    
    # Adjusted again based on feedback:
    # "a little more from the right"
    # x1: 280 -> 260
    crop_coords = (5, 660, 260, 745)
    
    print(f"Cropping with {crop_coords}...")
    success, result, size, out_path = apply_crop_with_coords(
        *crop_coords, 
        pdf_path, 
        section_name="debug_transit"
    )
    
    if success:
        print(f"Cropped to {out_path}")
        extractor = PDFTextExtractor()
        res = extractor.extract_all(out_path)
        print("\n--- Extracted Text ---")
        print(res['text'])
    else:
        print("Crop failed")

if __name__ == "__main__":
    test_crop_and_extract()
