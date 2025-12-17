"""
Test suite for Template 2 extraction generalizability.
Tests extraction on multiple Template 2 PDFs and validates results.
"""

import json
from pathlib import Path
from typing import Dict, List, Any
from collections import defaultdict


def test_all_template2_pdfs():
    """Test extraction on all Template 2 PDFs."""
    template2_dir = Path("template_2")
    output_dir = Path("output")
    
    if not template2_dir.exists():
        print(f"Template 2 directory not found: {template2_dir}")
        return
    
    # Find all Template 2 PDFs (excluding section PDFs in subdirectories)
    pdf_files = [f for f in template2_dir.glob("*.pdf") if not f.name.startswith(".")]
    
    if not pdf_files:
        print(f"No PDF files found in {template2_dir}")
        return
    
    print(f"=" * 70)
    print(f"Testing Template 2 Extraction Generalizability")
    print(f"Found {len(pdf_files)} PDF(s) to test")
    print(f"=" * 70)
    
    results = {}
    summary = defaultdict(lambda: {"total": 0, "extracted": 0, "missing": []})
    
    for pdf_file in sorted(pdf_files):
        print(f"\nTesting {pdf_file.name}...")
        try:
            # Check if output exists
            output_file = output_dir / f"{pdf_file.stem}_final_pipeline.json"
            
            if not output_file.exists():
                print(f"  [WARN] Output file not found: {output_file.name}")
                print(f"     Run pipeline first: python run_complete_pipeline.py {pdf_file}")
                results[pdf_file.name] = {"status": "not_processed", "error": "Output not found"}
                continue
            
            # Load and validate
            with open(output_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            validation = validate_extraction(data, pdf_file.name)
            results[pdf_file.name] = validation
            
            # Update summary
            for section, stats in validation.get("sections", {}).items():
                summary[section]["total"] += stats.get("total_fields", 0)
                summary[section]["extracted"] += stats.get("extracted_fields", 0)
                summary[section]["missing"].extend(stats.get("missing_fields", []))
            
            # Print results
            print(f"  [OK] Processed successfully")
            for section, stats in validation.get("sections", {}).items():
                extracted = stats.get("extracted_fields", 0)
                total = stats.get("total_fields", 0)
                if total > 0:
                    percentage = (extracted / total) * 100
                    print(f"     {section}: {extracted}/{total} fields ({percentage:.1f}%)")
                    if stats.get("missing_fields"):
                        print(f"       Missing: {', '.join(stats['missing_fields'][:3])}")
                        if len(stats['missing_fields']) > 3:
                            print(f"       ... and {len(stats['missing_fields']) - 3} more")
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
            results[pdf_file.name] = {"status": "error", "error": str(e)}
    
    # Print summary
    print(f"\n" + "=" * 70)
    print("Summary Statistics")
    print("=" * 70)
    
    for section, stats in summary.items():
        total = stats["total"]
        extracted = stats["extracted"]
        if total > 0:
            percentage = (extracted / total) * 100
            print(f"\n{section}:")
            print(f"  Total fields across all PDFs: {total}")
            print(f"  Successfully extracted: {extracted} ({percentage:.1f}%)")
            print(f"  Missing: {total - extracted}")
            
            # Most common missing fields
            if stats["missing"]:
                from collections import Counter
                missing_counts = Counter(stats["missing"])
                print(f"  Most common missing fields:")
                for field, count in missing_counts.most_common(5):
                    print(f"    - {field}: missing in {count} PDF(s)")
    
    return results


def validate_extraction(data: Dict, pdf_name: str) -> Dict:
    """Validate extracted data quality."""
    validation = {
        "pdf": pdf_name,
        "sections": {}
    }
    
    # Check bill_summary
    if "bill_summary_section" in data:
        bill_summary = data["bill_summary_section"].get("خلاصه صورتحساب", {})
        extracted = sum(1 for v in bill_summary.values() if v is not None)
        total = len(bill_summary)
        missing = [k for k, v in bill_summary.items() if v is None]
        
        validation["sections"]["bill_summary"] = {
            "total_fields": total,
            "extracted_fields": extracted,
            "missing_fields": missing,
            "extraction_rate": (extracted / total * 100) if total > 0 else 0
        }
    
    # Check consumption_history
    if "consumption_history_section" in data:
        consumption = data["consumption_history_section"].get("سوابق مصرف و مبلغ", [])
        rows = len(consumption) if isinstance(consumption, list) else 0
        
        validation["sections"]["consumption_history"] = {
            "total_rows": rows,
            "extracted_rows": rows,
            "extraction_rate": 100.0 if rows > 0 else 0
        }
    
    # Check ghodrat_kilowatt
    if "ghodrat_kilowatt_section" in data:
        ghodrat = data["ghodrat_kilowatt_section"].get("ghodrat_kilowatt_section", {})
        if not ghodrat:
            # Try alternative structure
            ghodrat = data["ghodrat_kilowatt_section"]
        
        extracted = sum(1 for v in ghodrat.values() if v is not None)
        total = len(ghodrat)
        missing = [k for k, v in ghodrat.items() if v is None]
        
        validation["sections"]["ghodrat_kilowatt"] = {
            "total_fields": total,
            "extracted_fields": extracted,
            "missing_fields": missing,
            "extraction_rate": (extracted / total * 100) if total > 0 else 0
        }
    
    # Check energy_supported
    if "energy_supported_section" in data:
        energy = data["energy_supported_section"].get("energy_supported_section", {})
        if not energy:
            energy = data["energy_supported_section"]
        
        rows = len(energy.get("rows", [])) if isinstance(energy, dict) else 0
        
        validation["sections"]["energy_supported"] = {
            "total_rows": rows,
            "extracted_rows": rows,
            "extraction_rate": 100.0 if rows > 0 else 0
        }
    
    # Check power_section
    if "power_section" in data:
        power = data["power_section"].get("power_section", {})
        if not power:
            power = data["power_section"]
        
        rows = len(power.get("rows", [])) if isinstance(power, dict) else 0
        
        validation["sections"]["power_section"] = {
            "total_rows": rows,
            "extracted_rows": rows,
            "extraction_rate": 100.0 if rows > 0 else 0
        }
    
    return validation


if __name__ == "__main__":
    results = test_all_template2_pdfs()
    
    # Save results to file
    output_file = Path("output") / "template2_test_results.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n[OK] Test results saved to: {output_file}")
