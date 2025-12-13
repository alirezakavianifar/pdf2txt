"""Check if crop box is set in cropped PDF."""
import fitz  # PyMuPDF
from pathlib import Path

# Check original PDF
original_pdf = Path("template1/1.pdf")
cropped_pdf = Path("template1/1/energy_supported_section.pdf")

print("=" * 70)
print("CROP BOX DETECTION")
print("=" * 70)

# Check original PDF
print(f"\nOriginal PDF: {original_pdf}")
doc = fitz.open(str(original_pdf))
page = doc[0]
media_box = page.mediabox
crop_box = page.cropbox
print(f"  Media box: ({media_box.x0}, {media_box.y0}, {media_box.x1}, {media_box.y1})")
print(f"  Crop box:  ({crop_box.x0}, {crop_box.y0}, {crop_box.x1}, {crop_box.y1})")
print(f"  Crop box == Media box: {crop_box == media_box}")
doc.close()

# Check cropped PDF
print(f"\nCropped PDF: {cropped_pdf}")
doc = fitz.open(str(cropped_pdf))
page = doc[0]
media_box = page.mediabox
crop_box = page.cropbox
print(f"  Media box: ({media_box.x0}, {media_box.y0}, {media_box.x1}, {media_box.y1})")
print(f"  Crop box:  ({crop_box.x0}, {crop_box.y0}, {crop_box.x1}, {crop_box.y1})")
print(f"  Crop box == Media box: {crop_box == media_box}")
print(f"  Crop box different: {crop_box != media_box}")
doc.close()
