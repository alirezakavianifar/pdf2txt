---
name: Template 4 Extraction Pipeline
overview: Add template_4 support to the PDF extraction pipeline by defining coordinates for keys identified in user images and creating specific restructure scripts.
todos:
  - id: analyze-coordinates
    content: Measure and define coordinates for 7 sections in config.py based on template_4/4.pdf
    status: todo
  - id: config-sections
    content: Add sections_template_4 to config.py
    status: todo
  - id: pipeline-template4
    content: Add process_template_4() function to run_complete_pipeline.py
    status: todo
  - id: restructure-power
    content: Create restructure_power_section_template4.py (for Power/Kilowatts section)
    status: todo
  - id: restructure-transformer
    content: Create restructure_transformer_coefficient_template4.py (for Transformer Coefficient)
    status: todo
  - id: restructure-license
    content: Create restructure_license_expiry_template4.py
    status: todo
  - id: restructure-consumption
    content: Create restructure_consumption_table_template4.py (for Consumption Table)
    status: todo
  - id: restructure-financial
    content: Create restructure_financial_table_template4.py (for Energy Cost/Financial Table)
    status: todo
  - id: restructure-period
    content: Create restructure_period_section_template4.py (Standard period info)
    status: todo
  - id: restructure-bill-id
    content: Create restructure_bill_identifier_template4.py (Standard bill ID)
    status: todo
  - id: test-pipeline
    content: Test pipeline with template_4/4.pdf and verify output
    status: todo
---

# Template 4 Extraction Pipeline Implementation

## Overview

Based on user-provided images from `template_4/4.pdf`, we need to extract specific data tables and values. The layout resembles other templates but requires specific coordinates and restructuring logic.

## Sections to Extract

Based on the images provided:

1.  **Power Section (Image 0)**
    *   Header: قدرت (کیلووات)
    *   Rows: قراردادی, پروانه مجاز, مصرفی, محاسبه شده, کاهش یافته, تجاوز از قدرت
    *   Values are numeric.

2.  **Transformer Coefficient (Image 1)**
    *   Text: ضریب ترانس 8000
    *   Value: 8000

3.  **License Expiry (Image 2)**
    *   Text: تاریخ انقضای پروانه : 1409/12/29
    *   Value: Date

4.  **Consumption Table (Image 3)**
    *   Headers: شرح مصارف ... میان باری, اوج بار, کم باری, اوج بار جمعه
    *   Columns: خرید از بورس, مصرف کل, شمارنده کنونی, شمارنده قبلی...

5.  **Financial/Energy Cost Table (Image 4)**
    *   Header: بهای انرژی (ریال)
    *   Columns: مصرف تامین شده, مشمول ماده 16, مشمول مابه التفاوت
    *   Rows: Matches consumption types (Mid, Peak, Low...)

6.  **Standard Sections** (Assumed present)
    *   `bill_identifier_section`: شناسه قبض
    *   `period_section`: اطلاعات دوره (From/To dates)

## Files to Modify

### 1. [config.py](config.py)
Add `sections_template_4` with coordinates for the above sections.
*Note: Coordinates need to be determined using `analyze_pdf_coordinates.py` or similar tool on `template_4/4.pdf`.*

### 2. [run_complete_pipeline.py](run_complete_pipeline.py)
Add `process_template_4()` function handling the cropping and calling the new restructure scripts.

## New Scripts to Create

### 3. `restructure_power_section_template4.py`
Extract key-value pairs from the Power section.

### 4. `restructure_transformer_coefficient_template4.py`
Extract the single coefficient value.

### 5. `restructure_license_expiry_template4.py`
Extract the date string.

### 6. `restructure_consumption_table_template4.py`
Parse the consumption table into structured list of dictionaries.

### 7. `restructure_financial_table_template4.py`
Parse the financial details table.

### 8. `restructure_period_section_template4.py`
Extract start date, end date, days.

### 9. `restructure_bill_identifier_template4.py`
Extract the bill identifier.

## Testing
Run: `python run_complete_pipeline.py template_4/4.pdf`
Verify `output/4_final_pipeline.json` contains all extracted data.
