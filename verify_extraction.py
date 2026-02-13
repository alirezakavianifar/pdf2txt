import os
import sys
from pathlib import Path
from run_complete_pipeline import run_pipeline

# Add project root to path
sys.path.append(str(Path.cwd()))

def verify_files():
    files_to_verify = [
        r"e:\projects\pdf2txt\23 ghabz\1000668903120.pdf",
        r"e:\projects\pdf2txt\23 ghabz\1001247601325.pdf",
        r"e:\projects\pdf2txt\23 ghabz\1001575401325.pdf"
    ]

    for file_path in files_to_verify:
        print(f"\n{'='*50}")
        print(f"Verifying: {file_path}")
        print(f"{'='*50}\n")
        
        path_obj = Path(file_path)
        if not path_obj.exists():
            print(f"ERROR: File not found: {file_path}")
            continue
            
        try:
            # Run the existing pipeline
            # Note: The pipeline saves output to 'output/<pdf_stem>'
            result = run_pipeline(str(path_obj))
            
            output_dir = Path("output") / path_obj.stem
            final_json = output_dir / f"{path_obj.stem}_final_pipeline.json"
            
            if final_json.exists():
                print(f"\nSUCCESS: generated {final_json}")
            else:
                print(f"\nFAILURE: json not found at {final_json}")
                
        except Exception as e:
            print(f"EXCEPTION processing {file_path}: {e}")

if __name__ == "__main__":
    verify_files()
