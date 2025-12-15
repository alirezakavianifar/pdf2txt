import sys
import json
import os
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
from restructure_transit_section import restructure_transit_section_json
from restructure_bill_identifier import restructure_bill_identifier_json
from restructure_energy_supported_template2 import restructure_energy_supported_template2_json
from restructure_power_section_template2 import restructure_power_section_template2_json
from restructure_ghodrat_kilowatt_template2 import restructure_ghodrat_kilowatt_template2_json
from restructure_consumption_history_template2 import restructure_consumption_history_template2_json
from restructure_bill_summary_template2 import (
    restructure_bill_summary_template2_json,
    restructure_bill_summary_template2_from_pdf,
)
from pdf_classifier import detect_template

def run_pipeline(pdf_filename="1.pdf"):
    print(f"\n--- Starting Full Pipeline for {pdf_filename} ---\n")
    
    # 0. Resolve Input Path
    # Handle paths with spaces and special characters
    input_pdf = Path(pdf_filename)
    
    # If path doesn't exist, try as absolute path first
    if not input_pdf.exists():
        # Try as absolute path if it looks like a full path
        if os.path.isabs(pdf_filename):
            input_pdf = Path(pdf_filename)
        else:
            # Try relative to current directory
            input_pdf = Path.cwd() / pdf_filename
    
    # If still doesn't exist, try fallback to template1 folder
    if not input_pdf.exists():
        # Only use template1 fallback if filename doesn't contain a path separator
        if os.sep not in pdf_filename and '/' not in pdf_filename:
            input_pdf = Path("template1") / pdf_filename
        else:
            # If it contains path separators, try relative to current directory
            input_pdf = Path.cwd() / pdf_filename
        
    if not input_pdf.exists():
        print(f"Error: {input_pdf} not found")
        print(f"  Searched for: {pdf_filename}")
        print(f"  Current directory: {Path.cwd()}")
        return

    # 1. Classification
    print(f"1. Classifying {input_pdf.name}...")
    try:
        template_id, confidence, details = detect_template(input_pdf)
        print(f"   Detected: {template_id} (Confidence: {confidence:.2f})")
        
        # Check if template matches configuration (currently hardcoded for template 1)
        if template_id not in ["template_1", "template1"]:
            print(f"   WARNING: Detected {template_id}, but pipeline is currently valid for Template 1.")
            print("   Proceeding, but cropping configuration might not match.")
            
    except Exception as e:
        print(f"   Classification failed: {e}")
        # Proceed anyway? Or return? Lets proceed as fallback
        
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    # Branch based on template
    if template_id in ["template_1", "template1"]:
        process_template_1(input_pdf, output_dir, template_id, confidence)
    elif template_id in ["template_2", "template2"]:
        process_template_2(input_pdf, output_dir, template_id, confidence)
    else:
        print(f"   WARNING: Unknown template {template_id}. Defaulting to Template 1 logic.")
        process_template_1(input_pdf, output_dir, template_id, confidence)

    print("\n--- Pipeline Complete ---")


def process_template_1(input_pdf, output_dir, template_id="template_1", confidence=1.0):
    """
    Process PDF using Template 1 logic (cropping and specific restructuring)
    """
    print(f"\n[Template 1 Process] Starting for {input_pdf.name}...")
    
    # 2. Crop
    print(f"2. Cropping {input_pdf.name} into sections...")
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
    print(f"\n3. Extracting and Restructuring...")
    extractor = PDFTextExtractor()
    merged_data = {
        "classification": {
            "template_id": template_id,
            "confidence": confidence
        }
    }
    intermediate_files = [] # Track files to clean up
    
    for name, pdf_path in cropped_files:
        print(f"\n  Processing {name}...")
        
        # Extract
        results = extractor.extract_all(str(pdf_path))
        base_name = f"{input_pdf.stem}_{name}"
        
        # Save raw
        extractor.save_results(results, output_dir, base_name)
        json_path = output_dir / f"{base_name}.json"
        intermediate_files.append(json_path)
        
        # Restructure
        restructured_path = output_dir / f"{base_name}_restructured.json"
        intermediate_files.append(restructured_path)
        
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
            elif name == "transit_section":
                data = restructure_transit_section_json(json_path, restructured_path)
            elif name == "bill_identifier_section":
                data = restructure_bill_identifier_json(json_path, restructured_path)
            else:
                print(f"    Warning: No restructure script for {name}")
                
            if data:
                merged_data.update(data)
                
        except Exception as e:
            print(f"    Error restructuring {name}: {e}")

    # 4. Save Final
    print(f"\n4. Saving Final Combined Output...")
    final_path = output_dir / f"{input_pdf.stem}_final_pipeline.json"
    
    with open(final_path, 'w', encoding='utf-8') as f:
        json.dump(merged_data, f, ensure_ascii=False, indent=2)
        
    print(f"  - Saved to {final_path}")
    print(f"  - Merged {len(merged_data)} sections/keys")
    
    # 5. Cleanup
    # 5. Cleanup
    print("\n5. Cleanup skipped (Debugging enabled)...")
    # for f_path in intermediate_files:
    #     try:
    #         if f_path.exists():
    #             f_path.unlink()
    #     except Exception as e:
    #         print(f"  Warning: Could not delete {f_path.name}: {e}")


def process_template_2(input_pdf, output_dir, template_id="template_2", confidence=1.0):
    """
    Process PDF using Template 2 logic
    """
    print(f"\n[Template 2 Process] Starting for {input_pdf.name}...")
    
    # 2. Crop
    print(f"2. Cropping {input_pdf.name} into sections (Template 2)...")
    cropped_files = []
    
    # Use Template 2 specific sections
    sections = default_config.crop.sections_template_2
    
    for section in sections:
        name = section['name']
        coords = (section['x0'], section['y0'], section['x1'], section['y1'])
        
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
    print(f"\n3. Extracting and Restructuring...")
    extractor = PDFTextExtractor()
    merged_data = {
        "classification": {
            "template_id": template_id,
            "confidence": confidence
        }
    }
    intermediate_files = [] # Track files to clean up
    
    for name, pdf_path in cropped_files:
        print(f"\n  Processing {name}...")
        
        # Extract
        results = extractor.extract_all(str(pdf_path))
        base_name = f"{input_pdf.stem}_{name}"
        
        # Save raw
        extractor.save_results(results, output_dir, base_name)
        json_path = output_dir / f"{base_name}.json"
        intermediate_files.append(json_path)
        
        # Restructure
        restructured_path = output_dir / f"{base_name}_restructured.json"
        intermediate_files.append(restructured_path)
        
        try:
            data = None
            # Map sections to their restructure functions
            # Assuming widely shared logic; if specific logic is needed, create new restructure scripts
            if name == "power_section":
                # Template 2 uses dedicated restructuring for power section
                data = restructure_power_section_template2_json(json_path, restructured_path)
            elif name == "period_section":
                data = restructure_period_section_json(json_path, restructured_path)
            elif name == "license_expiry_section":
                data = restructure_license_expiry_json(json_path, restructured_path)
            elif name == "energy_supported_section":
                # Template 2 uses dedicated restructuring for energy section
                data = restructure_energy_supported_template2_json(json_path, restructured_path)
            elif name == "bill_identifier_section":
                data = restructure_bill_identifier_json(json_path, restructured_path)
            elif name == "bill_summary_section":
                # Template 2 uses strip-based extraction directly from the cropped PDF
                data = restructure_bill_summary_template2_from_pdf(str(pdf_path), restructured_path)
            elif name == "consumption_history_section":
                # Template 2 uses dedicated restructuring for consumption history section
                data = restructure_consumption_history_template2_json(json_path, restructured_path)
            elif name == "ghodrat_kilowatt_section":
                # Template 2 uses dedicated restructuring for ghodrat_kilowatt section
                data = restructure_ghodrat_kilowatt_template2_json(json_path, restructured_path)
            else:
                print(f"    Warning: No restructure script for {name}")
                
            if data:
                merged_data.update(data)
                
        except Exception as e:
            print(f"    Error restructuring {name}: {e}")

    # 4. Save Final
    print(f"\n4. Saving Final Combined Output...")
    final_path = output_dir / f"{input_pdf.stem}_final_pipeline.json"
    
    with open(final_path, 'w', encoding='utf-8') as f:
        json.dump(merged_data, f, ensure_ascii=False, indent=2)
        
    print(f"  - Saved to {final_path}")
    print(f"  - Merged {len(merged_data)} sections/keys")
    
    # 5. Cleanup
    # 5. Cleanup
    print("\n5. Cleanup skipped (Debugging enabled)...")
    # for f_path in intermediate_files:
    #     try:
    #         if f_path.exists():
    #             f_path.unlink()
    #     except Exception as e:
    #         print(f"  Warning: Could not delete {f_path.name}: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        run_pipeline(sys.argv[1])
    else:
        run_pipeline("1.pdf")
