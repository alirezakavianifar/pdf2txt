# PDF to Text Extraction Pipeline

This document describes the complete data extraction pipeline for processing electricity bill PDFs.

## Overview

The pipeline extracts structured data from electricity bill PDFs through a multi-stage process:

1. **Classification** - Detect which template the PDF matches
2. **Cropping** - Split the PDF into named sections based on coordinates
3. **Extraction** - Extract text and tables from each section using `pdfplumber`
4. **Restructuring** - Parse and normalize extracted data into structured JSON
5. **Merging** - Combine all sections into a final output file

## Pipeline Architecture

```
┌─────────────────┐
│   Input PDF     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Classification │  ──► Detect Template (1 or 2)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│    Cropping     │  ──► Split into sections using coordinates from config.py
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────┐
│  For each cropped section:                              │
│  ┌─────────────┐    ┌──────────────┐    ┌────────────┐ │
│  │  Extract    │ ──►│  Restructure │ ──►│   Merge    │ │
│  │  (pdfplumber)│    │  (parsers)   │    │  (JSON)    │ │
│  └─────────────┘    └──────────────┘    └────────────┘ │
└─────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────┐
│  Final Output   │  ──► {pdf_name}_final_pipeline.json
└─────────────────┘
```

## Stage 1: Classification

**File:** `pdf_classifier/`

The pipeline first detects which template the PDF matches using the `detect_template()` function.

```python
from pdf_classifier import detect_template

template_id, confidence, details = detect_template(input_pdf)
# Returns: ("template_1", 0.95, {...}) or ("template_2", 0.92, {...})
```

Based on the detected template, the pipeline branches to use template-specific:

- Crop coordinates
- Restructuring scripts

## Stage 2: Cropping

**Files:** `adjust_crop.py`, `config.py`

The PDF is cropped into named sections using coordinates defined in `config.py`.

### Template 1 Sections

| Section Name                    | Description                                 | Coordinates (x0, y0, x1, y1) |
| ------------------------------- | ------------------------------------------- | ---------------------------- |
| `energy_supported_section`    | بهای انرژی پشتیبانی شده | (5, 90, 595, 262)            |
| `license_expiry_section`      | تاریخ انقضا پروانه          | (30, 40, 135, 65)            |
| `power_section`               | قدرت (کیلووات)                   | (420, 255, 590, 320)         |
| `period_section`              | اطلاعات دوره                     | (125, 255, 265, 285)         |
| `consumption_history_section` | سوابق مصرف و مبلغ             | (265, 330, 595, 420)         |
| `bill_summary_section`        | خلاصه صورتحساب                 | (15, 255, 130, 405)          |
| `transit_section`             | ترانزیت                              | (5, 660, 260, 745)           |
| `bill_identifier_section`     | شناسه قبض                           | (5, 505, 130, 525)           |

### Template 2 Sections

| Section Name                    | Description                                | Coordinates (x0, y0, x1, y1) |
| ------------------------------- | ------------------------------------------ | ---------------------------- |
| `bill_identifier_section`     | شناسه قبض                          | (20, 55, 180, 80)            |
| `license_expiry_section`      | تاریخ انقضا پروانه         | (340, 110, 550, 130)         |
| `energy_supported_section`    | جدول مصرف/انرژی               | (10, 165, 830, 260)          |
| `power_section`               | قدرت خریداری شده از نرخ | (240, 355, 580, 425)         |
| `period_section`              | اطلاعات دوره                    | (235, 280, 418, 315)         |
| `bill_summary_section`        | خلاصه مالی                        | (30, 280, 240, 360)          |
| `consumption_history_section` | سوابق مصرف                        | (230, 460, 825, 560)         |
| `ghodrat_kilowatt_section`    | قدرت - کیلووات                  | (600, 275, 830, 355)         |

Each section is saved as a separate cropped PDF file in the same directory as the input.

## Stage 3: Extraction

**File:** `extract_text.py`

The `PDFTextExtractor` class extracts data from each cropped PDF section.

### Extraction Methods

1. **Text Extraction** (`extract_text`)

   - Uses `pdfplumber` to extract words
   - Respects crop box coordinates
   - Sorts words by position (top→bottom, left→right)
   - Reconstructs text lines
2. **Table Extraction** (`extract_table`)

   - Extracts table structures into pandas DataFrames
   - Filters cells by crop region
   - Handles duplicate column names
3. **Geometry Extraction** (`GeometryExtractor`)

   - Extracts cell boundaries
   - Captures table structure (rows, columns)

### Text Normalization

**File:** `text_normalization.py`

All extracted text is normalized:

- **BIDI Processing** - Converts visual-order RTL text to logical-order
- **Persian Number Normalization** - Standardizes Persian/Arabic numerals
- **Whitespace Cleanup** - Removes extra spaces

### Output Format

Each section produces a JSON file with this structure:

```json
{
  "source_file": "power_section.pdf",
  "text": "قدرت (کیلووات)\nقراردادی: 2500\n...",
  "table": {
    "headers": ["col1", "col2", ...],
    "rows": [["val1", "val2"], ...],
    "row_count": 5,
    "column_count": 3
  },
  "table_info": {
    "rows": 5,
    "columns": 3
  }
}
```

## Stage 4: Restructuring

Each section's raw JSON is processed by a specialized restructuring script that parses the text/table data into a clean, typed structure.

### Restructuring Scripts

| Section                         | Template 1 Script                      | Template 2 Script                             |
| ------------------------------- | -------------------------------------- | --------------------------------------------- |
| `power_section`               | `restructure_power_section.py`       | `restructure_power_section_template2.py`    |
| `period_section`              | `restructure_period_section.py`      | (shared)                                      |
| `consumption_history_section` | `restructure_consumption_history.py` | (shared)                                      |
| `license_expiry_section`      | `restructure_license_expiry.py`      | (shared)                                      |
| `energy_supported_section`    | `restructure_complete.py`            | `restructure_energy_supported_template2.py` |
| `bill_summary_section`        | `restructure_bill_summary.py`        | (shared)                                      |
| `transit_section`             | `restructure_transit_section.py`     | N/A                                           |
| `bill_identifier_section`     | `restructure_bill_identifier.py`     | (shared)                                      |
| `ghodrat_kilowatt_section`    | N/A                                    | `restructure_complete.py` (generic)         |

### Example: Power Section (Template 1)

**Input:** Raw extracted text

```
قدرت (کیلووات)
قراردادی: 2500
دیماندی: 1800
محاسبه شده: 1850
```

**Output:** Structured JSON

```json
{
  "power_section": {
    "contractual_power": 2500,
    "demand_power": 1800,
    "calculated_power": 1850
  }
}
```

### Example: Power Section (Template 2)

**Input:** Raw extracted table with columns for different rate types

**Output:** Structured JSON

```json
{
  "power_section": {
    "table_type": "قدرت خریداری شده از نرخ",
    "rows": [
      {
        "category": "میان باری",
        "category_key": "mid_load",
        "bilateral": 100,
        "exchange": 50,
        "market_average": 75,
        "tou_hours": 8
      },
      ...
    ]
  }
}
```

## Stage 5: Merging

All restructured section data is merged into a single output dictionary:

```python
merged_data = {
    "classification": {
        "template_id": "template_1",
        "confidence": 0.95
    },
    "power_section": {...},
    "period_section": {...},
    "consumption_history_section": {...},
    "license_expiry_section": {...},
    "energy_supported_section": {...},
    "bill_summary_section": {...},
    "transit_section": {...},
    "bill_identifier_section": {...}
}
```

The final output is saved to: `output/{pdf_name}_finayl_pipeline.json`

## Usage

### Command Line

```bash
# Process a specific PDF
python run_complete_pipeline.py path/to/bill.pdf

# Process default (1.pdf in template1/)
python run_complete_pipeline.py
```

### Programmatic

```python
from run_complete_pipeline import run_pipeline

# Process a PDF
run_pipeline("path/to/bill.pdf")
```

## Configuration

All configuration is centralized in `config.py`:

```python
from config import default_config

# Crop coordinates
default_config.crop.sections           # Template 1 sections
default_config.crop.sections_template_2  # Template 2 sections

# Extraction settings
default_config.extraction.extract_tables  # Enable/disable table extraction
default_config.extraction.use_ocr         # Enable OCR fallback

# Normalization settings
default_config.normalization.handle_bidi              # BIDI text processing
default_config.normalization.normalize_persian_numbers  # Number normalization

# Output settings
default_config.output_formats  # ["json", "csv", "txt"]
```

## Dependencies

| Library            | Purpose                           |
| ------------------ | --------------------------------- |
| `pdfplumber`     | PDF text and table extraction     |
| `PyMuPDF (fitz)` | PDF cropping and crop box reading |
| `pandas`         | Table data handling               |
| `pydantic`       | Configuration models              |
| `python-bidi`    | RTL text processing               |

## File Structure

```
pdf2txt/
├── run_complete_pipeline.py    # Main entry point
├── config.py                   # Configuration
├── extract_text.py             # Text extraction
├── text_normalization.py       # BIDI & normalization
├── geometry_extraction.py      # Table geometry
├── adjust_crop.py              # PDF cropping
├── pdf_classifier/             # Template detection
│   └── __init__.py
├── restructure_*.py            # Section parsers
├── template1/                  # Template 1 sample PDFs
├── template_2/                 # Template 2 sample PDFs
└── output/                     # Extracted output files
```

## Error Handling

- **Classification failures** - Pipeline proceeds with fallback to Template 1
- **Crop failures** - Section is skipped, logged to console
- **Extraction errors** - Empty text returned, section skipped
- **Restructuring errors** - Exception logged, section skipped from merge

## Debugging

Intermediate files are preserved when debugging is enabled (default):

```python
# In run_complete_pipeline.py
print("\n5. Cleanup skipped (Debugging enabled)...")
```

This keeps:

- `{pdf}__{section}.json` - Raw extracted data
- `{pdf}__{section}_restructured.json` - Parsed structured data
