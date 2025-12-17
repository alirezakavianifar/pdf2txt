---
name: Template 5 Extraction Pipeline
overview: Add template_5 support to the PDF extraction pipeline by defining crop coordinates for 10 sections identified from template_5/5.pdf images, creating template-specific restructuring scripts, and updating the main pipeline to handle template_5 PDFs.
todos:
  - id: config-sections
    content: Add sections_template_5 to config.py with 10 section coordinates (coordinates need to be determined by analyzing template_5/5.pdf)
    status: completed
  - id: pipeline-template5
    content: Add process_template_5() function to run_complete_pipeline.py and update branching logic
    status: completed
    dependencies:
      - config-sections
  - id: restructure-company-info
    content: Create restructure_company_info_template5.py for company name, National ID, and location info
    status: completed
  - id: restructure-license
    content: Create restructure_license_expiry_template5.py for license expiry date
    status: completed
  - id: restructure-energy
    content: Create restructure_energy_consumption_template5.py for main consumption table with all columns
    status: completed
  - id: restructure-power
    content: Create restructure_power_section_template5.py for power values (قراردادی, محاسبه شده, etc.)
    status: completed
  - id: restructure-period
    content: Create restructure_period_section_template5.py for period information (دوره/سال, از تاریخ, تا تاریخ, به مدت)
    status: completed
  - id: restructure-reactive
    content: Create restructure_reactive_consumption_template5.py for reactive consumption and amount
    status: completed
  - id: restructure-summary
    content: Create restructure_bill_summary_template5.py for financial summary items
    status: completed
  - id: restructure-rate-diff
    content: Create restructure_rate_difference_template5.py for rate difference table
    status: completed
  - id: restructure-transit
    content: Create restructure_transit_section_template5.py for transit price
    status: completed
  - id: restructure-history
    content: Create restructure_consumption_history_template5.py for consumption history table with multiple periods
    status: completed
  - id: test-pipeline
    content: Test pipeline with template_5/5.pdf and verify all sections are extracted correctly
    status: pending
    dependencies:
      - pipeline-template5
      - restructure-company-info
      - restructure-license
      - restructure-energy
      - restructure-power
      - restructure-period
      - restructure-reactive
      - restructure-summary
      - restructure-rate-diff
      - restructure-transit
      - restructure-history
---

# Template 5 Extraction Pipeline Implementation

## Overview

Template 5 PDFs have a distinct layout with 10 sections that need extraction. Based on analysis of `template_5/5.pdf` images provided, the following sections have been identified. The PDF appears to be standard A4 size (595x842 points), similar to other templates.

## Section Coordinates (Template 5)

**Note:** Exact coordinates need to be determined by analyzing `template_5/5.pdf` using coordinate analysis tools. The following are estimated based on typical layouts and will need adjustment:

| Section | Description | Estimated Coordinates (x0, y0, x1, y1) | Notes |
|---------|-------------|------------------------------------------|-------|
| `company_info_section` | Company info & National ID (شناسه ملی) | (5, 5, 300, 50) | Top header with company name and National ID: ۱۰۸۶۰۱۰۰۱۶۷ |
| `license_expiry_section` | تاریخ انقضای پروانه | (60, 50, 200, 75) | License expiry date: ۱۴۰۳۱۲۳۹ |
| `energy_consumption_table_section` | جدول مصارف انرژی | (5, 75, 590, 250) | Main consumption table with rows: میان باری, اوج بار, کم باری, اوج بار جمعه |
| `power_section` | قدرت (کیلووات) | (350, 250, 590, 320) | Power values: قراردادی (2000), محاسبه شده, پروانه مجاز, کاهش یافته, میزان تجاوز از قدرت |
| `period_section` | اطلاعات دوره | (400, 250, 590, 300) | دوره/سال (۴/۷), از تاریخ, تا تاریخ, به مدت (۳۱ روز) |
| `reactive_consumption_section` | مصرف راکتیو | (200, 250, 350, 300) | Reactive consumption value: ۵۷,۲۱۰ |
| `bill_summary_section` | خلاصه صورتحساب | (5, 250, 200, 400) | Financial items: بهای انرژی تامین شده, بستانکاری خرید, ما بالتفاوت اجرای مقررات, etc. |
| `rate_difference_table_section` | مشمول ما بالتفاوت اجرای مقررات | (200, 300, 590, 400) | Table with rows: میان باری, اوج بار, کم باری, اوج بار جمعه |
| `transit_section` | ترانزیت | (400, 500, 590, 600) | Transit price: ۶۳۷,۷۴۳,۹۴۸ |
| `consumption_history_section` | سوابق مصارف مبالغ و پرداختهای ادوار گذشته | (5, 400, 590, 750) | History table with multiple periods |

## Files to Modify

### 1. [config.py](config.py) - Add template_5 sections

Add a new `sections_template_5` list with the 10 section coordinates. Place it after `sections_template_4` in the `CropConfig` class.

### 2. [run_complete_pipeline.py](run_complete_pipeline.py) - Add template_5 processing

Add a new `process_template_5()` function similar to `process_template_3()` and `process_template_4()`, and update the main branching logic to handle `template_5` and `template5` identifiers.

## New Scripts to Create

### 3. `restructure_company_info_template5.py`

Extract company information:

- Company name: شرکت توزیع نیروی برق استان بوشهر
- National ID (شناسه ملی): ۱۰۸۶۰۱۰۰۱۶۷
- City/Region: شهر ناحیه (برازجان)
- Address: آدرس
- Region: منطقه برق (برازجان)
- Incident unit: واحد حوادث (۷۷۳۴۲۴۹۶۰۰)
- Bill parcel code: پارچگویچ صورتحساب

### 4. `restructure_license_expiry_template5.py`

Extract license expiry date (تاریخ انقضای پروانه) - date like `۱۴۰۳۱۲۳۹` (format: YYYYMMDD).

### 5. `restructure_energy_consumption_template5.py`

Parse the main energy consumption table with columns:

- شرح مصارف (Description): میان باری, اوج بار, کم باری, اوج بار جمعه
- شمارنده قبلی (Previous Counter)
- شمارنده کنونی (Current Counter)
- رقم (Digit)
- ضریب (Coefficient): ۳,۰۰۰
- مصرف (Kwh) (Consumption)
- مشمول تجدید پذیر (Renewable Included)
- خرید تجدید پذیر (Renewable Purchase)
- تولید تجدید پذیر (Renewable Production)
- خرید بورس و دو جانبه (Exchange and Bilateral Purchase)
- مصرف تامین شده به نیابت (Consumption Supplied by Proxy) - with sub-columns: مصرف, نرخ
- بهای انرژی (Energy Price)

### 6. `restructure_power_section_template5.py`

Extract power values:

- قراردادی (Contractual): ۲۰۰۰
- محاسبه شده (Calculated): ۰
- پروانه مجاز (Authorized License): ۰
- کاهش یافته (Reduced): ۰
- میزان تجاوز از قدرت (Amount of power exceeding limit): ۰
- مصرفی (Consumed): ۵۱۳.۳۰۰۰

### 7. `restructure_period_section_template5.py`

Extract period information:

- دوره/سال (Period/Year): ۴/۷ (period 4, year 7 of 1404)
- از تاریخ (From Date): ۱۴۰۴/۰۶/۰۱
- تا تاریخ (To Date): ۱۴۰۴/۰۷/۰۱
- به مدت (Duration): ۳۱ روز (31 days)

### 8. `restructure_reactive_consumption_template5.py`

Extract reactive consumption (مصرف راکتیو) - value like `۵۷,۲۱۰` and reactive amount (مبلغ راکتیو).

### 9. `restructure_bill_summary_template5.py`

Extract financial summary items:

- بهای انرژی تامین شده: 18,236,250
- بستانکاری خرید: -25,322,420 (negative value)
- ما بالتفاوت اجرای مقررات: 821,761,655
- آبونمان: 143,481
- هزینه سوخت نیروگاهی: 96,036,403
- تعدیل بهای برق: 55,664,049
- عوارض برق: 257,171,074
- مالیات بر ارزش افزوده: 91,085,537

### 10. `restructure_rate_difference_template5.py`

Parse the rate difference table with:

- Header: مشمول ما بالتفاوت اجرای مقررات
- Rows: میان باری, اوج بار, کم باری, اوج بار جمعه
- Columns: شرح مصارف, مصرف, مبلغ, خرید بورس آزاد

### 11. `restructure_transit_section_template5.py`

Extract transit section data:

- بهای ترانزیت: ۶۳۷,۷۴۳,۹۴۸

### 12. `restructure_consumption_history_template5.py`

Parse the consumption history table with:

- Header: سوابق مصارف مبالغ و پرداختهای ادوار گذشته
- Columns: دوره/سال, تاریخ قرائت, مصارف کیلووات ساعت (میان باری, اوج بار, کم باری, اوج بار جمعه, راکتیو), مبلغ دوره ریال, مهلت پرداخت, مبلغ پرداختی, تاریخ پرداخت
- Multiple rows for different periods

## Implementation Notes

1. Each restructuring script follows the existing pattern:

- `convert_persian_digits()` for number normalization
- `parse_decimal_number()` or `parse_number()` for parsing values
- Main function that reads JSON, parses text, returns structured dict
- Save to `{base_name}_restructured.json`

2. The classifier already has a `template_5.json` signature file, so detection should work automatically.

3. All 10 sections are unique to template_5 layout, hence new scripts for each.

4. **Coordinate Determination**: Before implementation, coordinates must be determined by:

- Using `analyze_pdf_coordinates.py` or similar tool on `template_5/5.pdf`
- Or manually inspecting the PDF with coordinate extraction tools
- Adjusting estimated coordinates based on actual PDF layout

5. The energy consumption table is complex with many columns - may require careful parsing of table structure from extracted text/table data.

6. The consumption history table spans multiple periods and may be quite large - ensure coordinates capture the full table.

## Testing

Test with: `python run_complete_pipeline.py template_5/5.pdf`

Expected output: `output/5_final_pipeline.json` with all 10 sections merged.

## Dependencies

- All restructuring scripts should import from existing utilities:
- `convert_persian_digits()` from any existing template script
- `parse_number()` or `parse_decimal_number()` from existing scripts
- Standard JSON and Path handling