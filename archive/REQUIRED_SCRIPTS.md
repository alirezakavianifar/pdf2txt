# Required Scripts for run_complete_pipeline.py

## Overview
This document lists all scripts that are **required** for `run_complete_pipeline.py` to function properly.

## Core Pipeline Scripts (7 files)

1. **`run_complete_pipeline.py`** ⭐ Main entry point
   - Orchestrates the entire pipeline
   - Handles Template 1 and Template 2 processing

2. **`adjust_crop.py`**
   - PDF cropping functionality
   - Used to extract sections from PDFs

3. **`config.py`**
   - Configuration and crop coordinates
   - Defines sections for Template 1 and Template 2

4. **`extract_text.py`**
   - Text and table extraction from PDFs
   - Main extraction class: `PDFTextExtractor`

5. **`text_normalization.py`**
   - Text normalization utilities
   - Used by `extract_text.py`
   - Class: `TextNormalizer`

6. **`geometry_extraction.py`**
   - Geometry extraction utilities
   - Used by `extract_text.py`
   - Class: `GeometryExtractor`

7. **`pdf_classifier/`** (Directory)
   - PDF template classification
   - Module: `pdf_classifier`
   - Function: `detect_template()`

## Template 1 Restructuring Scripts (8 files)

8. **`restructure_power_section.py`**
   - Function: `restructure_power_section_json()`
   - Used for: `power_section` in Template 1

9. **`restructure_consumption_history.py`**
   - Function: `restructure_consumption_history_json()`
   - Used for: `consumption_history_section` in Template 1

10. **`restructure_period_section.py`**
    - Function: `restructure_period_section_json()`
    - Used for: `period_section` in **both** templates

11. **`restructure_license_expiry.py`**
    - Function: `restructure_license_expiry_json()`
    - Used for: `license_expiry_section` in **both** templates

12. **`restructure_complete.py`**
    - Function: `restructure_json()`
    - Used for: `energy_supported_section` in Template 1

13. **`restructure_bill_summary.py`**
    - Function: `restructure_bill_summary_json()`
    - Used for: `bill_summary_section` in Template 1

14. **`restructure_transit_section.py`**
    - Function: `restructure_transit_section_json()`
    - Used for: `transit_section` in Template 1

15. **`restructure_bill_identifier.py`**
    - Function: `restructure_bill_identifier_json()`
    - Used for: `bill_identifier_section` in **both** templates

## Template 2 Restructuring Scripts (5 files)

16. **`restructure_energy_supported_template2.py`**
    - Function: `restructure_energy_supported_template2_json()`
    - Used for: `energy_supported_section` in Template 2

17. **`restructure_power_section_template2.py`**
    - Function: `restructure_power_section_template2_json()`
    - Used for: `power_section` in Template 2

18. **`restructure_ghodrat_kilowatt_template2.py`**
    - Function: `restructure_ghodrat_kilowatt_template2_json()`
    - Used for: `ghodrat_kilowatt_section` in Template 2

19. **`restructure_consumption_history_template2.py`**
    - Function: `restructure_consumption_history_template2_json()`
    - Used for: `consumption_history_section` in Template 2

20. **`restructure_bill_summary_template2.py`**
    - Function: `restructure_bill_summary_template2_json()`
    - Used for: `bill_summary_section` in Template 2

## Summary

- **Total Required Scripts:** 20 Python files + 1 directory (`pdf_classifier/`)
- **Core Pipeline:** 7 files
- **Template 1 Specific:** 6 files
- **Template 2 Specific:** 5 files
- **Shared (Both Templates):** 3 files (`restructure_period_section.py`, `restructure_license_expiry.py`, `restructure_bill_identifier.py`)

## Archived Scripts

The following scripts have been moved to `archive/` as they are **not required** for the pipeline:

### Test Scripts
- `test_6_pdfs.py`
- `test_template2_generalizability.py`
- `test_crop_transit.py`
- `generate_test_report.py`

### Utility/Development Scripts
- `display_power_results.py`
- `find_coords.py`
- `find_transit_coords.py`

### Old Restructuring Scripts
- Various old versions and experimental restructuring scripts (already in archive)

## Verification

To verify all required scripts are present, run:
```bash
python -c "import run_complete_pipeline; print('All imports successful')"
```

If all required scripts are present, this should complete without errors.
