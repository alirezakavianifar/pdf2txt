"""Test script to extract from template1/1.pdf"""
from pathlib import Path
from extract_text import PDFTextExtractor
import json

# Initialize extractor
extractor = PDFTextExtractor()

# Extract from template1/1.pdf
pdf_path = Path("template1/1.pdf")
print(f"Extracting from: {pdf_path}")
print(f"File exists: {pdf_path.exists()}")

# Extract all data
results = extractor.extract_all(str(pdf_path), page_num=0)

# Check if crop box was detected
crop_bbox = extractor.get_crop_box_from_pdf(str(pdf_path), page_num=0)
print(f"\nCrop box detected: {crop_bbox}")

# Save to test output
output_dir = Path("output")
output_dir.mkdir(exist_ok=True)
extractor.save_results(results, output_dir, "test_1_original")

# Print summary
print(f"\nExtraction Summary:")
print(f"  Text length: {len(results['text'])} characters")
print(f"  Table extracted: {results.get('table_df') is not None}")
if results.get('table_df') is not None:
    print(f"  Table shape: {results['table_df'].shape}")
print(f"  Geometry extracted: {results.get('geometry') is not None}")

# Show first 500 chars of text
print(f"\nFirst 500 characters of extracted text:")
print(results['text'][:500])