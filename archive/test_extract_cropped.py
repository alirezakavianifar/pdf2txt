"""Test script to extract from cropped PDF."""
from pathlib import Path
from extract_text import PDFTextExtractor
import json

# Create extractor
extractor = PDFTextExtractor()

# Process the cropped PDF
cropped_pdf = Path("template1/1/energy_supported_section.pdf")
output_dir = Path("output")

print(f"Processing cropped PDF: {cropped_pdf}")
print(f"Output directory: {output_dir}")

# Extract all data
results = extractor.extract_all(str(cropped_pdf))

# Check if crop box was detected
crop_bbox = extractor.get_crop_box_from_pdf(str(cropped_pdf))
print(f"\nCrop box detected: {crop_bbox}")

# Save results
extractor.save_results(results, output_dir, "1_cropped_test")

# Print summary
print(f"\n{'='*70}")
print(f"Extraction Summary:")
print(f"{'='*70}")
print(f"Text length: {len(results.get('text', ''))} characters")
print(f"Table extracted: {results.get('table_df') is not None}")
if results.get('table_df') is not None:
    print(f"Table shape: {results.get('table_df').shape}")
