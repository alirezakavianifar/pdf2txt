import json
import sys
from pathlib import Path
from run_complete_pipeline import run_pipeline

def debug_template1(pdf_path):
    print(f"Running extraction on {pdf_path}")
    
    try:
        # Run pipeline
        merged_data = run_pipeline(str(pdf_path), export_excel=False)
        
        # Print the keys in the merged data to understand the structure
        print("\nExtracted Data Keys:")
        print(merged_data.keys())
        
        # Capture checks in a list to write to file
        output_lines = []
        
        target_values = ["312363713", "343600084", "446", "530", "1404/06/01", "1404/07/01", "31", "367.8", "821880", "1404/07/07", "0.0736"]
        output_lines.append(f"\n--- Searching for {target_values} in extracted data ---")
        
        # Helper to search recursively
        def search_dict(d, path=""):
            for k, v in d.items():
                current_path = f"{path}.{k}" if path else k
                str_v = str(v)
                for val in target_values:
                    if val in str_v:
                        output_lines.append(f"Found {val} in key: {current_path}")
                        output_lines.append(f"Value: {v}")
                
                if isinstance(v, dict):
                    search_dict(v, current_path)
                elif isinstance(v, list):
                    for i, item in enumerate(v):
                        if isinstance(item, dict):
                            search_dict(item, f"{current_path}[{i}]")
                        else:
                            str_item = str(item)
                            for val in target_values:
                                if val in str_item:
                                    output_lines.append(f"Found {val} in list: {current_path}[{i}]")
                                    output_lines.append(f"Value: {item}")
                            
        search_dict(merged_data)
            
        output_lines.append("\n--- Full merged data ---")
        output_lines.append(json.dumps(merged_data, ensure_ascii=False, indent=2))

        # Also check the raw output files for intermediate data
        output_dir = Path("output") / Path(pdf_path).stem
        output_lines.append(f"\nChecking output directory: {output_dir}")
        if output_dir.exists():
            for json_file in output_dir.glob("*_restructured.json"):
                output_lines.append(f"Checking {json_file.name}...")
                with open(json_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    for val in target_values:
                        if val in content:
                            output_lines.append(f"  FOUND {val} in {json_file.name}")
                            
        with open("debug_t1_output_utf8.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(output_lines))
        print("Output written to debug_t1_output_utf8.txt")

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
        debug_template1(pdf_file)
