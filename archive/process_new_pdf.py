"""Process a specific PDF file."""
from pathlib import Path
from extract_text import PDFTextExtractor

extractor = PDFTextExtractor()
pdf_path = Path("template1/4_550_9000310904123/energy_supported_section.pdf")
output_dir = Path("output")
pdf_folder = pdf_path.parent.name
section_name = pdf_path.stem
output_base_name = f"{pdf_folder}_{section_name}"

print(f"Processing: {pdf_path}")
results = extractor.extract_all(str(pdf_path))
extractor.save_results(results, output_dir, output_base_name)
print(f"Extraction complete: {output_dir}/{output_base_name}.json")
