"""Test consumption history section extraction on all PDFs."""
from pathlib import Path
from extract_text import PDFTextExtractor
from restructure_consumption_history import restructure_consumption_history_json

def process_pdf(pdf_path: Path, output_dir: Path):
    """Process a single PDF: extract and restructure."""
    extractor = PDFTextExtractor()
    
    pdf_folder = pdf_path.parent.name
    section_name = pdf_path.stem
    output_base_name = f"{pdf_folder}_{section_name}"
    
    print(f"\n{'='*60}")
    print(f"Processing: {pdf_folder}/{pdf_path.name}")
    print(f"{'='*60}")
    
    try:
        # Extract
        results = extractor.extract_all(str(pdf_path))
        extractor.save_results(results, output_dir, output_base_name)
        
        # Restructure
        extracted_json = output_dir / f"{output_base_name}.json"
        restructured_json = output_dir / f"{output_base_name}_restructured.json"
        
        if extracted_json.exists():
            restructure_consumption_history_json(extracted_json, restructured_json)
            return True
        else:
            print(f"ERROR: Extraction failed - {extracted_json.name} not found")
            return False
    except Exception as e:
        print(f"ERROR processing {pdf_path.name}: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    # Find all consumption_history_section.pdf files
    template_dir = Path("template1")
    pdf_files = list(template_dir.glob("*/consumption_history_section.pdf"))
    
    if not pdf_files:
        print("No consumption_history_section.pdf files found in template1/")
        # Try to find by PDF names provided
        pdf_names = [
            "1",
            "4_510_9019722204129",
            "4_550_9000310904123",
            "4_550_9000896204125",
            "4_550_9402898804120",
            "4_567_9004439404122",
            "4_600_9000796904120",
            "4_600_9001713204128",
            "4_600_9001869604126",
            "4_600_9002420604128"
        ]
        
        for pdf_name in pdf_names:
            pdf_path = template_dir / pdf_name / "consumption_history_section.pdf"
            if pdf_path.exists():
                pdf_files.append(pdf_path)
    
    print(f"\nFound {len(pdf_files)} PDF files to process")
    
    results_summary = []
    for pdf_path in sorted(pdf_files):
        success = process_pdf(pdf_path, output_dir)
        results_summary.append((pdf_path.parent.name, success))
    
    # Print summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    for pdf_name, success in results_summary:
        status = "SUCCESS" if success else "FAILED"
        print(f"{pdf_name}: {status}")
    
    success_count = sum(1 for _, s in results_summary if s)
    print(f"\nTotal: {success_count}/{len(results_summary)} successful")

