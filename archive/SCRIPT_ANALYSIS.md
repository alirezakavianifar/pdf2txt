# Script Analysis for run_complete_pipeline.py

## Required Scripts (Used in Pipeline)

### Core Pipeline Scripts
1. **`run_complete_pipeline.py`** - Main pipeline orchestrator
2. **`adjust_crop.py`** - PDF cropping functionality
3. **`config.py`** - Configuration and crop coordinates
4. **`extract_text.py`** - Text and table extraction from PDFs
5. **`text_normalization.py`** - Text normalization (used by extract_text)
6. **`geometry_extraction.py`** - Geometry extraction (used by extract_text)
7. **`pdf_classifier/`** - PDF template classification

### Template 1 Restructuring Scripts
8. **`restructure_power_section.py`** - Power section for Template 1
9. **`restructure_consumption_history.py`** - Consumption history for Template 1
10. **`restructure_period_section.py`** - Period section (used by both templates)
11. **`restructure_license_expiry.py`** - License expiry (used by both templates)
12. **`restructure_complete.py`** - Energy supported section for Template 1
13. **`restructure_bill_summary.py`** - Bill summary for Template 1
14. **`restructure_transit_section.py`** - Transit section for Template 1
15. **`restructure_bill_identifier.py`** - Bill identifier (used by both templates)

### Template 2 Restructuring Scripts
16. **`restructure_energy_supported_template2.py`** - Energy supported for Template 2
17. **`restructure_power_section_template2.py`** - Power section for Template 2
18. **`restructure_ghodrat_kilowatt_template2.py`** - Ghodrat kilowatt for Template 2
19. **`restructure_consumption_history_template2.py`** - Consumption history for Template 2
20. **`restructure_bill_summary_template2.py`** - Bill summary for Template 2

## Scripts to Archive (Not Used in Pipeline)

### Test Scripts
- `test_6_pdfs.py` - Test script for 6 PDFs
- `test_template2_generalizability.py` - Generalizability test
- `test_crop_transit.py` - Transit cropping test
- `generate_test_report.py` - Test report generator

### Utility/Development Scripts
- `display_power_results.py` - Display utility
- `find_coords.py` - Coordinate finding utility
- `find_transit_coords.py` - Transit coordinate utility

## Archive Status

Scripts already in `archive/` folder:
- Various old restructuring scripts (already archived)
- Old versions of restructuring scripts

## Action Plan

1. Move test scripts to `archive/`
2. Move utility scripts to `archive/`
3. Keep all restructuring scripts that are used
4. Document the required scripts
