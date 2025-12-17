# Archive Summary

## Files Archived

The following files have been moved to the `archive/` directory as they are **not required** for `run_complete_pipeline.py` to function:

### Test Scripts
- ✅ `test_6_pdfs.py` - Test script for 6 PDFs
- ✅ `test_template2_generalizability.py` - Generalizability test
- ✅ `test_crop_transit.py` - Transit cropping test
- ✅ `generate_test_report.py` - Test report generator

### Utility/Development Scripts
- ✅ `display_power_results.py` - Display utility
- ✅ `find_coords.py` - Coordinate finding utility
- ✅ `find_transit_coords.py` - Transit coordinate utility

## Files Remaining in Root

All remaining Python files in the root directory are **required** for the pipeline:

### Core Pipeline (7 files)
1. `run_complete_pipeline.py` ⭐
2. `adjust_crop.py`
3. `config.py`
4. `extract_text.py`
5. `text_normalization.py`
6. `geometry_extraction.py`
7. `pdf_classifier/` (directory)

### Template 1 Restructuring (8 files)
8. `restructure_power_section.py`
9. `restructure_consumption_history.py`
10. `restructure_period_section.py`
11. `restructure_license_expiry.py`
12. `restructure_complete.py`
13. `restructure_bill_summary.py`
14. `restructure_transit_section.py`
15. `restructure_bill_identifier.py`

### Template 2 Restructuring (5 files)
16. `restructure_energy_supported_template2.py`
17. `restructure_power_section_template2.py`
18. `restructure_ghodrat_kilowatt_template2.py`
19. `restructure_consumption_history_template2.py`
20. `restructure_bill_summary_template2.py`

## Verification

✅ All required scripts are present and imports are successful.

The pipeline is ready to use with only the necessary scripts in the root directory.
