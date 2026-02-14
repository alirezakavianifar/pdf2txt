import json
import sys
from pathlib import Path
from run_complete_pipeline import run_pipeline

def debug_template1_check(pdf_path):
    print(f"Running extraction on {pdf_path}")
    
    try:
        # Run pipeline
        merged_data = run_pipeline(str(pdf_path), export_excel=False)
        
        print("\n--- Extracted Article 16 Keys ---")
        found_any = False
        for key, value in merged_data.items():
            if "ماده 16" in key:
                print(f"{key}: {value}")
                found_any = True
        
        if not found_any:
            print("No 'Article 16' (ماده 16) keys found in merged data.")

        # Check raw text for numbers if extraction failed
        output_dir = Path("output") / Path(pdf_path).stem
        energy_json = output_dir / f"{Path(pdf_path).stem}_energy_supported_section.json"
        
        if energy_json.exists():
             with open(energy_json, 'r', encoding='utf-8') as f:
                data = json.load(f)
                text = data.get('text', '')
                print("\n--- Text Snippet from Energy Supported Section ---")
                # Look for the numbers from the image: 54462, 2296, 56758
                nums = ["54462", "2296", "56758"]
                for line in text.split('\n'):
                    if any(n in line for n in nums):
                        print(f"Found line with target numbers: {line}")

    except Exception as e:
        print(f"Error during extraction: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Force utf-8 output for terminal
    sys.stdout.reconfigure(encoding='utf-8')
    
    pdf_file = Path("template1/4_550_9000896204125.pdf")
    if not pdf_file.exists():
        print(f"File {pdf_file} does not exist!")
    else:
        debug_template1_check(pdf_file)
