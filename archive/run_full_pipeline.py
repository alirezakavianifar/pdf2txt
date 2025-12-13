"""Run full pipeline: extract and restructure for a PDF."""
from pathlib import Path
from extract_text import PDFTextExtractor
from restructure_complete import restructure_json

def process_pdf_full(pdf_path: Path, output_dir: Path = None):
    """Process PDF: extract and restructure."""
    extractor = PDFTextExtractor()
    
    if output_dir is None:
        output_dir = Path("output")
    
    # Extract
    pdf_folder = pdf_path.parent.name
    section_name = pdf_path.stem
    output_base_name = f"{pdf_folder}_{section_name}"
    
    print(f"Processing: {pdf_folder}/{pdf_path.name}")
    results = extractor.extract_all(str(pdf_path))
    extractor.save_results(results, output_dir, output_base_name)
    
    # Restructure
    extracted_json = output_dir / f"{output_base_name}.json"
    restructured_json = output_dir / f"{output_base_name}_restructured.json"
    
    if extracted_json.exists():
        restructure_json(extracted_json, restructured_json)
        print(f"\nFull pipeline complete!")
        print(f"  Extracted: {extracted_json.name}")
        print(f"  Restructured: {restructured_json.name}")
    
    return results

if __name__ == "__main__":
    # Process the requested PDF
    pdf_path = Path("template1/4_550_9000310904123/energy_supported_section.pdf")
    process_pdf_full(pdf_path)
