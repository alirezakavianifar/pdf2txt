---
name: Template 6 Extraction Pipeline
overview: Document the complete template_6 extraction pipeline structure, including 8 section coordinates, restructuring scripts, and data fields to extract from template_6 PDFs based on the example 6.pdf.
todos:
  - id: verify-sections
    content: Verify all 8 section coordinates in config.py are correctly defined for template_6 layout
    status: completed
  - id: verify-pipeline
    content: Verify process_template_6() function correctly calls all restructuring scripts
    status: completed
  - id: test-company-info
    content: Test restructure_company_info_template6.py extracts all company fields correctly
    status: completed
  - id: test-license-expiry
    content: Test restructure_license_expiry_template6.py extracts date 1407/10/22
    status: completed
  - id: test-energy-table
    content: Test restructure_energy_consumption_template6.py extracts all 14 columns for 5 row types
    status: completed
  - id: test-power-section
    content: Test restructure_power_section_template6.py extracts all 6 power values
    status: completed
  - id: test-period-section
    content: Test restructure_period_section_template6.py extracts all 5 period fields
    status: completed
  - id: test-bill-summary
    content: Test restructure_bill_summary_template6.py extracts all 23 financial items
    status: completed
  - id: test-transit-section
    content: Test restructure_transit_section_template6.py extracts all 7 transit fields
    status: completed
  - id: test-consumption-history
    content: Test restructure_consumption_history_template6.py extracts table with all columns and rows
    status: completed
  - id: test-full-pipeline
    content: Test complete pipeline with template_6/6.pdf and verify final JSON output
    status: completed
    dependencies:
      - verify-sections
      - verify-pipeline
  - id: validate-extracted-data
    content: Validate extracted data matches expected values from template_6/6.pdf example
    status: completed
    dependencies:
      - test-full-pipeline
isProject: false
---

# Template 6 Extraction Pipeline Implementation

## Overview

Template 6 PDFs have a distinct layout with 8 sections that need extraction. Based on analysis of `template_6/6.pdf` (595x842 points), the following sections have been identified with their coordinates and data extraction requirements.

## Section Coordinates (Template 6)


| Section                            | Description                                                 | Coordinates (x0, y0, x1, y1) |
| ---------------------------------- | ----------------------------------------------------------- | ---------------------------- |
| `company_info_section`             | Company info & National ID (شناسه ملی)                      | (5, 5, 300, 50)              |
| `license_expiry_section`           | License Expiry Date (تاریخ انقضای پروانه)                   | (60, 50, 200, 75)            |
| `energy_consumption_table_section` | Energy Consumption Table (جدول مصارف انرژی)                 | (5, 75, 590, 250)            |
| `power_section`                    | Power Section (قدرت - کیلووات)                              | (350, 250, 590, 320)         |
| `period_section`                   | Period Information (اطلاعات دوره)                           | (400, 250, 590, 300)         |
| `bill_summary_section`             | Bill Summary (خلاصه صورتحساب)                               | (5, 250, 200, 450)           |
| `transit_section`                  | Transit Section (صورتحساب ترانزیت)                          | (400, 500, 590, 650)         |
| `consumption_history_section`      | Consumption History (سوابق مصارف، مبالغ و پرداخت های مشترک) | (5, 400, 590, 750)           |


## Files Already Configured

### 1. [config.py](config.py) - Template 6 sections

The `sections_template_6` list contains all 8 section coordinates defined above.

### 2. [run_complete_pipeline.py](run_complete_pipeline.py) - Template 6 processing

The `process_template_6()` function handles:

- Cropping PDF into 8 sections using coordinates from `config.py`
- Extracting text and tables from each section
- Calling appropriate restructuring scripts for each section
- Merging all sections into final output JSON

## Restructuring Scripts

### 3. `restructure_company_info_template6.py`

Extract company information:

- Company name: توزیع برق گلستان
- National ID (شناسه ملی): 411,140,441,069
- Economic code (کد اقتصادی)
- Subscription code (شتراک): 605508116
- Address (آدرس)
- Region (منطقه برق)
- Unit code (واحد حوادث)
- Meter body number (شمارده بدنه کنتور): 120597550000240
- Meter coefficient (ضریب کنتور): 4,000
- Voltage code (کد ولتاژ)
- Activity code (کد فعالیت)
- Tariff code (کد تعرفه): 4420
- Option code (کد گزینه): 1
- Computer code (رمز رایانه): 60550811614022

### 4. `restructure_license_expiry_template6.py`

Extract license expiry date (تاریخ انقضای پروانه) - date like `1407/10/22`.

### 5. `restructure_energy_consumption_template6.py`

Parse the main energy consumption table with 14 columns:

**Row Types:**

- میان بار (Mid-load)
- اوج بار (Peak Load)
- کم بار (Off-peak Load)
- جمعه (Friday)
- راکتیو (Reactive)

**Columns:**

- شرح مصارف (Description)
- شمارنده قبلی (Previous Counter)
- شمارنده فعلی (Current Counter)
- تعداد ارقام (Number of Digits): 6
- ضریب کنتور (Meter Coefficient): 4,000
- انرژی قرائت شده (Read Energy)
- انرژی خریداری شده دوجانبه و بورس (Energy Purchased Bilaterally and from Exchange)
- انرژی مازاد خرید از بازار (Excess Energy Purchased from Market)
- انرژی خریداری شده دو جانبه سبز (Green Bilaterally Purchased Energy)
- مصرف قانون جهش تولید (Consumption under Production Leap Law)
- انرژی تامین شده توسط توزیع (Energy Supplied by Distribution)
- بهای انرژی تامین شده توسط توزیع (Cost of Energy Supplied by Distribution)
- انرژی مشمول تعرفه (۴- الف) (Energy Subject to Tariff 4-A)
- انرژی مشمول تعرفه (۴-د) (Energy Subject to Tariff 4-D)

**Example Data:**

- میان بار: Previous: 13,596.35, Current: 13,691.83, Read Energy: 381,920
- اوج بار: Previous: 4,079.96, Current: 4,138.89, Read Energy: 235,720
- کم بار: Previous: 8,650.68, Current: 8,753.84, Read Energy: 412,640
- راکتیو: Previous: 5,711.34, Current: 5,779.05, Read Energy: 270,840

### 6. `restructure_power_section_template6.py`

Extract power values:

- قراردادی (Contractual): 2,500
- قدرت مجاز (Permitted Power): 2,500
- قدرت قرائت (Read Power): 1,766
- قدرت فراتش (Exceeded Power): 1,766
- محاسبه شده (Calculated): 1,766
- تجاوز از قدرت (Power Exceeded): 2,250

### 7. `restructure_period_section_template6.py`

Extract period information:

- از تاریخ (From Date): 1404/06/01
- تا تاریخ (To Date): 1404/07/01
- تعداد روز (Number of Days): 31
- دوره/سال (Period/Year): 1404/6
- تاریخ صورتحساب (Invoice Date): 1404/07/15

### 8. `restructure_bill_summary_template6.py`

Extract financial summary items:

- بهای انرژی (Energy Price): 7,781,378
- بهای قدرت (Power Price)
- مابه التفاوت اجرای (Implementation Difference): 2,687,341,132
- آبونمان (Subscription Fee): 143,481
- تفاوت تعرفه انشعاب (Branch Tariff Difference)
- تجاوز از قدرت (Power Exceeded)
- پیک فصل (Peak Season)
- بهای انرژی راکتیو (Reactive Energy Price)
- انقضای پروانه (License Expiration)
- مبلغ تبصره ی 14 (Amount of Note 14): 415,225,586
- مابه التفاوت انرژی مشمول ماده 16 (Energy Difference Subject to Article 16)
- پاداش همکاری (Cooperation Bonus)
- بستانکاری خرید خارج بازار (Credit for Off-Market Purchase): -792,620,046
- تعدیل بهای برق (Electricity Price Adjustment)
- بیمه (Insurance)
- بیمه عمومی (Public Insurance)
- عوارض برق (Electricity Charges): 1,082,009,606
- مالیات بر ارزش افزوده (Value Added Tax): 231,787,153
- وجه التزام (Penalty)
- بهای برق دوره (Period Electricity Price): 3,631,668,290
- بدهکاری / بستانکاری (Debt/Credit): -26,202,700,169
- کسر هزار ریال (Thousand Rial Deduction)
- مبلغ قابل پرداخت (Payable Amount)

### 9. `restructure_transit_section_template6.py`

Extract transit section data:

- هزینه ترانزیت (Transit Cost): 449,844,512
- ترانزیت فوق توزیع (Super Distribution Transit): 1,049,637,194
- حق العمل کاری (Commission/Labor Fee)
- تعدیل بهای برق (Electricity Price Adjustment)
- مالیات بر ارزش افزوده (Value Added Tax): 149,948,170
- بدهی گذشته (Past Debt)
- وجه التزام (Penalty/Liquidated Damages)

### 10. `restructure_consumption_history_template6.py`

Parse the consumption history table with:

- Header: سوابق مصارف، مبالغ و پرداخت های مشترک
- Columns: دوره, تاریخ قرائت, مصرف اکتیو, مصرف راکتیو, مبلغ دوره, مبلغ پرداختی, تاریخ پرداخت
- Rows: Historical consumption data with dates and amounts

**Example Data:**

- Period: 04/04, Reading Date: 1404/05/01, Active Consumption: (dot), Reactive Consumption: 483,800, Period Amount: 24,448,747,443
- Period: 04/05, Reading Date: 1404/06/01, Active Consumption: 55,307, Reactive Consumption: 408,720, Period Amount: 24,232,868,584
- Period: 04/06, Reading Date: 1404/07/01, Active Consumption: 1,878, Reactive Consumption: 270,840, Period Amount: 3,631,668,290

## Implementation Notes

1. Each restructuring script follows the existing pattern:

- `convert_persian_digits()` for number normalization
- `parse_number()` or `parse_decimal_number()` for parsing values
- Main function that reads JSON, parses text/tables, returns structured dict

1. The classifier should have a `template_6.json` signature file for detection.
2. All 8 sections are unique to template_6 layout, with dedicated restructuring scripts for each.
3. The energy consumption table is complex with 14 columns and requires careful table parsing to extract all values correctly.
4. Some fields may contain dots (.) indicating zero or not applicable - these should be handled gracefully.

## Testing

Test with: `python run_complete_pipeline.py template_6/6.pdf`

Expected output: `output/6_final_pipeline.json` with all 8 sections merged:

- Company info
- License expiry
- Energy consumption table
- Power section
- Period section
- Bill summary
- Transit section
- Consumption history

## Data Validation

Verify extracted data matches the example from `template_6/6.pdf`:

- License expiry: 1407/10/22
- Period: From 1404/06/01 to 1404/07/01 (31 days)
- Power: Contractual 2,500, Read 1,766
- Energy consumption table has 5 rows (میان بار, اوج بار, کم بار, جمعه, راکتیو)
- Bill summary contains all financial items
- Transit section has transit costs
- Consumption history has 3 rows of historical data

