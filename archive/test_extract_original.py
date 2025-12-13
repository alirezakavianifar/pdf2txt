"""
Test script to extract from original PDF (1.pdf) to verify crop box handling.
"""
from pathlib import Path
from extract_text import PDFTextExtractor
import json

# Create extractor
extractor = PDFTextExtractor()

# Process the original PDF
original_pdf = Path("template1/1.pdf")
output_dir = Path("output")

print(f"Processing original PDF: {original_pdf}")
print(f"Output directory: {output_dir}")

# Extract all data
results = extractor.extract_all(str(original_pdf))

# Check if crop box was detected
crop_bbox = extractor.get_crop_box_from_pdf(str(original_pdf))
print(f"\nCrop box detected: {crop_bbox}")

# Save results
extractor.save_results(results, output_dir, "1_original_test")

# Print summary
print(f"\n{'='*70}")
print(f"Extraction Summary:")
print(f"{'='*70}")
print(f"Text length: {len(results.get('text', ''))} characters")
print(f"Table extracted: {results.get('table_df') is not None}")
if results.get('table_df') is not None:
    print(f"Table shape: {results.get('table_df').shape}")
print(f"Geometry extracted: {results.get('geometry') is not None}")

# Show first 500 characters of text
if results.get('text'):
    print(f"\nFirst 500 characters of extracted text:")
    print("-" * 70)
    print(results['text'][:500])
    print("-" * 70)
