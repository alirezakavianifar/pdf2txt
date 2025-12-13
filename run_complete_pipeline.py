import sys
import json
from pathlib import Path

# Add current directory to path to ensure imports work
sys.path.append(str(Path.cwd()))

from adjust_crop import apply_crop_with_coords
from config import default_config
from extract_text import PDFTextExtractor
from restructure_power_section import restructure_power_section_json
from restructure_consumption_history import restructure_consumption_history_json
from restructure_period_section import restructure_period_section_json
from restructure_license_expiry import restructure_license_expiry_json
from restructure_complete import restructure_json
from restructure_bill_summary import restructure_bill_summary_json

def run_pipeline(pdf_filename="1.pdf"):
    print(f"\n--- Starting Full Pipeline for {pdf_filename} ---\n")
    
    # 1. Setup
    input_pdf = Path("template1") / pdf_filename
    if not input_pdf.exists():
        print(f"Error: {input_pdf} not found")
        return
        
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    # 2. Crop
    print(f"1. Cropping {pdf_filename} into sections...")
    cropped_files = []
    
    for section in default_config.crop.sections:
        name = section['name']
        coords = (section['x0'], section['y0'], section['x1'], section['y1'])
        
        # apply_crop_with_coords(x0, y0, x1, y1, input_pdf, output_pdf=None, section_name="cropped")
        success, result, size, out_path = apply_crop_with_coords(
            *coords, 
            str(input_pdf), 
            section_name=name
        )
        
        if success:
            print(f"  - Cropped {name}: {out_path}")
            cropped_files.append((name, Path(out_path)))
        else:
            print(f"  - Failed to crop {name}: {result}")

    # 3. Extract & Restructure
    print(f"\n2. Extracting and Restructuring...")
    extractor = PDFTextExtractor()
    merged_data = {}
    
    for name, pdf_path in cropped_files:
        print(f"\n  Processing {name}...")
        
        # Extract
        results = extractor.extract_all(str(pdf_path))
        base_name = f"{input_pdf.stem}_{name}"
        
        # Save raw
        extractor.save_results(results, output_dir, base_name)
        
        # Restructure
        json_path = output_dir / f"{base_name}.json"
        restructured_path = output_dir / f"{base_name}_restructured.json"
        
        try:
            data = None
            if name == "power_section":
                data = restructure_power_section_json(json_path, restructured_path)
            elif name == "period_section":
                data = restructure_period_section_json(json_path, restructured_path)
            elif name == "consumption_history_section":
                data = restructure_consumption_history_json(json_path, restructured_path)
            elif name == "license_expiry_section":
                data = restructure_license_expiry_json(json_path, restructured_path)
            elif name == "energy_supported_section":
                data = restructure_json(json_path, restructured_path)
            elif name == "bill_summary_section":
                data = restructure_bill_summary_json(json_path, restructured_path)
            else:
                print(f"    Warning: No restructure script for {name}")
                
            if data:
                merged_data.update(data)
                
        except Exception as e:
            print(f"    Error restructuring {name}: {e}")

    # 4. Save Final
    print(f"\n3. Saving Final Combined Output...")
    final_path = output_dir / f"{input_pdf.stem}_final_pipeline.json"
    
    with open(final_path, 'w', encoding='utf-8') as f:
        json.dump(merged_data, f, ensure_ascii=False, indent=2)
        
    print(f"  - Saved to {final_path}")
    print(f"  - Merged {len(merged_data)} sections/keys")
    print("\n--- Pipeline Complete ---")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        run_pipeline(sys.argv[1])
    else:
        run_pipeline("1.pdf")
