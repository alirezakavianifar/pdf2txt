"""Process a specific PDF file and create restructured output."""
from pathlib import Path
from extract_text import PDFTextExtractor
import json

# Initialize extractor
extractor = PDFTextExtractor()

# Set output directory
output_dir = Path("output")

# Process the cropped PDF
pdf_path = Path("template1/4_510_9019722204129/energy_supported_section.pdf")
pdf_folder = pdf_path.parent.name  # "4_510_9019722204129"
section_name = pdf_path.stem       # "energy_supported_section"
output_base_name = f"{pdf_folder}_{section_name}"

print(f"Processing: {pdf_path}")
print(f"Output base name: {output_base_name}")

# Extract all data
results = extractor.extract_all(str(pdf_path))

# Save raw extraction results
extractor.save_results(results, output_dir, output_base_name)

print(f"\nExtraction complete. Saved to: {output_dir}/{output_base_name}.json")
