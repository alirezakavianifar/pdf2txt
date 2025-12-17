---
name: Template 3 Extraction Pipeline
overview: Add template_3 support to the PDF extraction pipeline by defining crop coordinates for 9 sections, creating template-specific restructuring scripts, and updating the main pipeline to handle template_3 PDFs.
todos:
  - id: config-sections
    content: Add sections_template_3 to config.py with 9 section coordinates
    status: done
  - id: pipeline-template3
    content: Add process_template_3() function to run_complete_pipeline.py
    status: done
  - id: restructure-bill-id
    content: Create restructure_bill_identifier_template3.py
    status: done
  - id: restructure-license
    content: Create restructure_license_expiry_template3.py
    status: done
  - id: restructure-energy
    content: Create restructure_energy_consumption_template3.py
    status: done
  - id: restructure-power
    content: Create restructure_power_section_template3.py
    status: done
  - id: restructure-period
    content: Create restructure_period_section_template3.py
    status: done
  - id: restructure-reactive
    content: Create restructure_reactive_consumption_template3.py
    status: done
  - id: restructure-summary
    content: Create restructure_bill_summary_template3.py
    status: done
  - id: restructure-rate-diff
    content: Create restructure_rate_difference_template3.py
    status: done
  - id: restructure-transit
    content: Create restructure_transit_section_template3.py
    status: done
  - id: test-pipeline
    content: Test pipeline with template_3/3.pdf and verify output
    status: done
---

# Template 3 Extraction Pipeline Implementation

## Overview

Template 3 PDFs have a distinct layout with 9 sections that need extraction. Based on analysis of `template_3/3.pdf` (595x842 points), the following sections have been identified with their coordinates.

## Section Coordinates (Template 3)

| Section | Description | Coordinates (x0, y0, x1, y1) |
|---------|-------------|------------------------------|
| `bill_identifier_section` | شناسه قبض | (5, 35, 160, 70) |
| `license_expiry_section` | تاریخ انقضا پروانه | (60, 80, 160, 100) |
| `energy_consumption_table_section` | جدول مصارف انرژی | (5, 125, 590, 230) |
| `power_section` | قدرت (کیلووات) | (345, 225, 590, 280) |
| `period_section` | اطلاعات دوره | (445, 275, 590, 310) |
| `reactive_consumption_section` | مصرف راکتیو | (260, 275, 370, 310) |
| `bill_summary_section` | خلاصه صورتحساب | (5, 230, 155, 430) |
| `rate_difference_table_section` | شرح مصارف و مابه التفاوت | (148, 315, 580, 400) |
| `transit_section` | ترانزیت | (430, 590, 590, 690) |

## Files to Modify

### 1. [config.py](config.py) - Add template_3 sections

Add a new `sections_template_3` list with the 9 section coordinates.

### 2. [run_complete_pipeline.py](run_complete_pipeline.py) - Add template_3 processing

Add a new `process_template_3()` function similar to `process_template_1()` and `process_template_2()`, and update the main branching logic.

## New Scripts to Create

### 3. `restructure_bill_identifier_template3.py`

Extract bill identifier (شناسه قبض) - value like `7030899411120`.

### 4. `restructure_license_expiry_template3.py`

Extract license expiry date (تاریخ انقضا پروانه) - date like `1499/12/29`.

### 5. `restructure_energy_consumption_template3.py`

Parse the main energy consumption table with columns:

- شرح مصارف (Description)
- شمارنده قبلی/کنونی (Counters)
- ضریب (Coefficient)
- مصرف کل (Total Consumption)
- مصرف مشمول/غیرمشمول قانون جهش تولید
- انرژی خریداری شده (Purchased Energy)
- بهای انرژی (Energy Cost)

### 6. `restructure_power_section_template3.py`

Extract power values:

- قراردادی (Contractual): 3000
- ماکسیمتر (Maximator): 804
- مجاز (Permitted): 3000
- محاسبه شده (Calculated): 3216
- مصرفی (Consumed): 3216
- کاهش یافته (Reduced)

### 7. `restructure_period_section_template3.py`

Extract period information:

- از تاریخ (From Date): 1403/09/01
- تا تاریخ (To Date): 1403/10/01
- تعداد روز دوره (Days): 30
- دوره/سال (Period/Year): 1403/10

### 8. `restructure_reactive_consumption_template3.py`

Extract reactive consumption (مصرف راکتیو) - value like `568000`.

### 9. `restructure_bill_summary_template3.py`

Extract financial summary items:

- بهای انرژی تامین شده: 19,549,842
- آبونمان: 129,769
- تفاوت تعرفه انشعاب آزاد: 0
- تجاوز از قدرت: 5,884,226,942
- هزینه سوخت نیروگاهی: 464,987,520
- عوارض برق: 1,743,143,496
- مابه التفاوت ماده16 و ماده 3: 1,288,569,600
- مبلغ دوره: 11,670,335,410
- مالیات بر ارزش افزوده: 992,719,192
- بدهکاری/بستانکاری: 21,759,206,375
- کسر هزار ریال: -23

### 10. `restructure_rate_difference_template3.py`

Parse the rate difference table with:

- Header: شرح مصارف و مابه التفاوت نرخ تجدیدپذیر
- Rows: میان باری, اوج بار, کم باری, اوج بار جمعه
- Columns: مصرف مشمول, خرید از نیروگاه, خرید از تابلو سبز, تولید, مصرف قابل محاسبه, نرخ, مبلغ

### 11. `restructure_transit_section_template3.py`

Extract transit section data:

- حق العمل: 0
- ترانزیت: 1,557,187,200
- اصلاح تعرفه دیرکرد
- مالیات بر ارزش افزوده ترانزیت: 155,718,720
- بهای برق دوره: 1,712,905,920
- بدهکاری/بستانکاری: 1,677,471,561
- کسر هزار ریال: 481

## Implementation Notes

1. Each restructuring script follows the existing pattern:

- `convert_persian_digits()` for number normalization
- `parse_decimal_number()` for parsing values
- Main function that reads JSON, parses text, returns structured dict

2. The classifier already has a `template_3.json` signature file, so detection should work.

3. All 9 sections are unique to template_3 layout, hence new scripts for each.

## Testing

Test with: `python run_complete_pipeline.py template_3/3.pdf`

Expected output: `output/3_final_pipeline.json` with all 9 sections merged.