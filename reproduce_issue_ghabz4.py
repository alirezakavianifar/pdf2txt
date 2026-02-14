from run_complete_pipeline import run_pipeline
from pathlib import Path
import json

def reproduce():
    pdf_path = Path(r"e:\projects\pdf2txt\23 ghabz\مشکلدار\ghabz (4).pdf")
    if not pdf_path.exists():
        print(f"File not found: {pdf_path}")
        return

    print(f"Running pipeline on {pdf_path}")
    result = run_pipeline(str(pdf_path))
    
    # helper to print specific keys
    if result:
        print("\n--- Extracted Data (Snippet) ---")
        keys_to_check = [
            "bill_summary", "amount_summary", "financial_details", 
            "energy_cost", "subscription", "power_plant_fuel_cost",
            "late_payment_adjustment", "electricity_levies", "vat",
            "total_period", "debit", "fraction_of_rial"
        ]
        
        # recursive search for keys
        def print_keys(data, indent=0):
            for k, v in data.items():
                if any(target in k for target in keys_to_check) or k in keys_to_check:
                    print(" " * indent + f"{k}: {v}")
                if isinstance(v, dict):
                    print_keys(v, indent + 2)
        
        # print_keys(result) # This might me too verbose if keys are nested deeply without matching
        
        # Let's just dump the relevant sections if we can find them
        # Based on the image, we are looking for bill summary or financial info
        
        sections = ["bill_summary", "transit_section", "financial_info"]
        for section in sections:
            if section in result:
                print(f"\n--- {section} ---")
                print(json.dumps(result[section], indent=2, ensure_ascii=False))
            
            # Also check at root level
            for k, v in result.items():
                if section in k:
                     print(f"\n--- {k} ---")
                     print(json.dumps(v, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    reproduce()
