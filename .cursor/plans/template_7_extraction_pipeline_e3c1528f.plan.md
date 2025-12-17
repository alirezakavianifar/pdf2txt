---
name: Template 7 Extraction Pipeline
overview: Add template_7 support to the PDF extraction pipeline by defining crop coordinates for 9 sections identified from template_7/7.pdf images, creating template-specific restructuring scripts, and updating the main pipeline to handle template_7 PDFs.
todos:
  - id: config-sections
    content: Add sections_template_7 to config.py with 9 section coordinates (coordinates need to be determined by analyzing template_7/7.pdf)
    status: completed
  - id: pipeline-template7
    content: Add process_template_7() function to run_complete_pipeline.py and update branching logic
    status: completed
    dependencies:
      - config-sections
  - id: restructure-bill-id
    content: Create restructure_bill_identifier_template7.py for bill ID (شناسه قبض)
    status: completed
  - id: restructure-license
    content: Create restructure_license_expiry_template7.py for license expiry date
    status: completed
  - id: restructure-company-info
    content: Create restructure_company_info_template7.py for company and customer information
    status: completed
  - id: restructure-energy
    content: Create restructure_energy_consumption_template7.py for main consumption table with all columns
    status: completed
  - id: restructure-power
    content: Create restructure_power_section_template7.py for power values and meter specifications
    status: completed
  - id: restructure-period
    content: Create restructure_period_section_template7.py for period information (دوره/سال, از تاریخ, تا تاریخ, به مدت)
    status: completed
  - id: restructure-summary
    content: Create restructure_bill_summary_template7.py for financial summary items
    status: completed
  - id: restructure-history
    content: Create restructure_consumption_history_template7.py for consumption history table with multiple periods
    status: completed
  - id: restructure-transit
    content: Create restructure_transit_section_template7.py for transit costs and rates
    status: completed
  - id: restructure-rate-diff
    content: Create restructure_rate_difference_template7.py for rate difference information (optional)
    status: completed
  - id: test-pipeline
    content: Test pipeline with template_7/7.pdf and verify all sections are extracted correctly
    status: pending
    dependencies:
      - pipeline-template7
      - restructure-bill-id
      - restructure-license
      - restructure-company-info
      - restructure-energy
      - restructure-power
      - restructure-period
      - restructure-summary
      - restructure-history
      - restructure-transit
---

# Template 7 Extraction Pipeline Implementation

## Overview

Template 7 PDFs have a distinct layout with 9 sections that need extraction. Based on analysis of `template_7/7.pdf` images provided and the extracted text, the following sections have been identified. The PDF appears to be standard A4 size (612x792 points) with 2 pages.

## Section Coordinates (Template 7)

**Note:** Exact coordinates need to be determined by analyzing `template_7/7.pdf` using coordinate analysis tools. The following are estimated based on typical layouts and will need adjustment:

| Section | Description | Estimated Coordinates (x0, y0, x1, y1) | Notes |
|---------|-------------|------------------------------------------|-------|
| `bill_identifier_section` | شناسه قبض (Bill ID) | (5, 5, 200, 30) | Bill ID: 7791699307222 |
| `license_expiry_section` | تاریخ انقضا پروانه (License Expiry Date) | (5, 30, 200, 55) | License expiry date: 1500/01/01 |
| `company_info_section` | Company Information | (5, 5, 400, 80) | Company: شرکت توزیع برق استان قزوین, Customer: شرکت ستاره بافت نگارین ارغوان |
| `energy_consumption_table_section` | جدول مصارف انرژی (Energy Consumption Table) | (5, 80, 590, 280) | Complex table with: میان باری, اوج باری, کم باری, اوج بار جمعه, راکتیو |
| `power_section` | قدرت (کیلووات) (Power Section) | (400, 280, 590, 350) | Power values: قراردادی (1200), مجاز (1200), مصرفی (659.68), ماکسیمتر (0.412) |
| `period_section` | اطلاعات دوره (Period Information) | (400, 350, 590, 380) | از تاریخ (1404/06/01), تا تاریخ (1404/07/01), به مدت (31) |
| `bill_summary_section` | خلاصه صورتحساب (Bill Summary) | (5, 280, 400, 450) | Financial items: آبونمان, هزینه سوخت نیروگاهی, ما به التفاوت اجرای مقررات, etc. |
| `consumption_history_section` | سوابق مصرف، مبالغ و پرداخت های دوره های گذشته | (5, 450, 590, 700) | History table with multiple periods |
| `transit_section` | ترانزیت (Transit Section) | (400, 450, 590, 550) | Transit costs: ترانزیت توزیع, ترانزیت برق منطقه ای |

## Files to Modify

### 1. [config.py](config.py) - Add template_7 sections

Add a new `sections_template_7` list with the 9 section coordinates. Place it after `sections_template_6` in the `CropConfig` class.

### 2. [run_complete_pipeline.py](run_complete_pipeline.py) - Add template_7 processing

Add a new `process_template_7()` function similar to `process_template_3()` and `process_template_4()`, and update the main branching logic to handle `template_7` and `template7` identifiers.

## New Scripts to Create

### 3. `restructure_bill_identifier_template7.py`

Extract bill identifier (شناسه قبض) - value like `7791699307222`.

### 4. `restructure_license_expiry_template7.py`

Extract license expiry date (تاریخ انقضا پروانه) - date like `1500/01/01`.

### 5. `restructure_company_info_template7.py`

Extract company and customer information:

- Company name: شرکت توزیع برق استان قزوین
- City/Region: شهر امور (قزوین جنوب)
- Address: جاده الموت جاده اشنستان جنب ثامن بتن
- Region: منطقه برق (قزوین جنوب)
- Unit code: واحد حوادث (33239260)
- Customer name: شرکت ستاره بافت نگارین ارغوان
- Consumption address: نشانی محل مصرف
- Correspondence address: نشانی محل مکاتباتی
- Postal code: کد پستی (3414739866)
- Economic code: کد اقتصادی
- National ID: شناسه ملی
- Payment ID: شناسه پرداخت (288170640708)
- Identification: شناسایی (10/42/06/029700)
- File number: پرونده (10145867)
- Subscription number: شماره اشتراک (7916993)
- Installation date: تاریخ نصب (1381/04/24)
- Tariff code: عنوان و کد تعرفه ([4410] [4-4] صنعتی الف)
- Activity code: کد فعالیت (418801/ انواع کیسه)
- Activity type: نوع فعالیت (418801/ انواع کیسه)
- Selected option: گزینه انتخابی (3)
- Computer code: رمز رایانه (7916993)
- Supply voltage: ولتاژ تغذیه (فشار ضعیف - 38)

### 6. `restructure_energy_consumption_template7.py`

Parse the main energy consumption table with complex structure:

**Row Types:**

- میان باری (Mid-load)
- اوج باری (Peak-load)
- کم باری (Off-peak load)
- اوج بار جمعه (Friday Peak-load)
- راکتیو (Reactive)

**Columns:**

- مصرف کنتور (Meter Consumption): 181600, 87760, 92512, 0, 361872, 36944
- آیین نامه سبز (Green Regulations):
- درصد ماده 16 (Article 16 Percentage)
- خرید سبز (Green Purchase)
- نرخ مابه التفاوت ماده 16 (Article 16 Difference Rate)
- مبلغ مابه التفاوت ماده 16 (Article 16 Difference Amount)
- خرید دو جانبه - بورس (Bilateral Purchase - Stock Exchange): 183,768, 91,884, 91,884, 0, 367,536
- مصرف تامین شده به نیابت (Consumption Supplied by Proxy):
- مصرف (Consumption): 2168-, 4124-, 628
- مبلغ (Amount): 2601295.32
- بستانکاری مازاد خرید انرژی (Credit for Excess Energy Purchase): 2928426-, 5579772-, 8508198-
- مشمول مابه التفاوت (Subject to Difference):
- مصرف (Consumption): 181600, 87760, 92512, 0, 269360
- مبلغ (Amount): 462,032,168, 705,084,025, 0, 0, 1,167,116,193
- بهای انرژی (ریال) (Energy Price): 0, 0, 2,601,295, 0, 2,601,295

### 7. `restructure_power_section_template7.py`

Extract power values:

- قراردادی (Contractual): 1200
- مجاز (Permitted): 1200
- مصرفی (Consumed): 659.68
- ماکسیمتر (Maximator): 0.412
- محاسبه شده (Calculated): (empty or 0)
- کاهش یافته (Reduced): (empty or 0)
- میزان تجاوز از قدرت (Amount of power exceeding): 0
- تاریخ اتمام کاهش موقت (Temporary Reduction End Date): 1500/01/01

**Meter Specifications:**

- شماره بدنه کنتور اکتیو (Active Meter Body Number): 18059877002170
- شماره بدنه کنتور راکتیو (Reactive Meter Body Number): 18059877002170
- ضریب کنتور (Meter Coefficient): 1600
- ضریب قدرت (Power Coefficient): 0.99
- میزان تجاوز از قدرت (Power Exceeded Amount): 0

### 8. `restructure_period_section_template7.py`

Extract period information:

- از تاریخ (From Date): 1404/06/01
- تا تاریخ (To Date): 1404/07/01
- به مدت (Duration): 31 (days)
- تاریخ صدور صورتحساب (Invoice Issue Date): 1404/07/30
- کل مصرف (Total Consumption): 361872

### 9. `restructure_bill_summary_template7.py`

Extract financial summary items:

- آبونمان (Subscription Fee): 143,481
- هزینه سوخت نیروگاهی (Power Plant Fuel Cost): 153,960,087
- بهای انرژی راکتیو (Reactive Energy Price): 0
- بهای فصل (Seasonal Price): 0
- ما به التفاوت اجرای مقررات (Regulation Implementation Difference): 1,167,116,193
- بهای برق تامین شده به نیابت (Electricity Price Supplied by Proxy): 2,601,295.32
- بستانکاری مازاد خرید انرژی (Credit for Excess Energy Purchase): 8,508,198- (negative)
- مبلغ مابه التفاوت ماده 16 (سبز) (Article 16 Difference Amount - Green): 0
- عوارض برق (Electricity Tariffs): 355,610,298
- مالیات بر ارزش افزوده (Value Added Tax): 131,531,286
- مبلغ بدهی ماده 3 (Article 3 Debt Amount): 1/24
- بدهکار / بستانکار (Debtor/Creditor): 1,079,251,557
- کسر هزار ریال (Thousand Rial Deduction): 796
- مبلغ قابل پرداخت (Payable Amount): 2,881,706,000
- مهلت پرداخت (Payment Deadline): (date)
- مشمول قطع (Subject to Disconnection): (yes/no)

### 10. `restructure_consumption_history_template7.py`

Parse the consumption history table with:

- Header: سوابق مصرف، مبالغ و پرداخت های دوره های گذشته
- Columns: دوره/سال, تاریخ قرائت, میان باری, اوج باری, کم باری, اوج بار جمعه, راکتیو, (مبلغ دوره) ریال, مهلت پرداخت
- Multiple rows for different periods

**Example Data:**

- Period: 10406, Reading Date: 1404/06/01, Mid-load: 4627.51, Peak-load: 1499.67, Off-peak: 2967.13, Friday: 66.1805, Reactive: 1142.37, Period Amount: 1,776,186,788, Payment Deadline: 1404/06/12
- Period: 10405, Reading Date: 1404/05/01, Mid-load: 4515.66, Peak-load: 1445.25, Off-peak: 2908.92, Friday: 66.1805, Reactive: 1116.48, Period Amount: 1,895,300,254, Payment Deadline: 1404/05/10

### 11. `restructure_transit_section_template7.py`

Extract transit section data:

- ترانزیت توزیع (Distribution Transit): 168,075,118
- ترانزیت برق منطقه ای (Regional Electricity Transit): 392,175,274
- مالیات بر ارزش افزوده (Value Added Tax): 56,025,039
- بدهکار / بستانکار (Debtor/Creditor): 616,274,476- (negative)
- کسر هزار ریال (Thousand Rial Deduction): 955
- نرخ ترانزیت توزیع (Distribution Transit Rate): 246564
- نرخ ترانزیت برق منطقه ای (Regional Electricity Transit Rate): 575316

### 12. `restructure_rate_difference_template7.py` (Optional)

Extract rate difference information if present:

- نرخ صنعتی (Industrial Rate): میان باری (5490), اوج باری (10980), کم باری (2945.77)
- نرخ مابه التفاوت اجرای مقررات (Regulation Implementation Difference Rate): میان باری (2544.23), اوج باری (8034.23), کم باری (0)
- متوسط قیمت تابلو اول بورس (Average First Exchange Board Price): میان باری (1801), اوج باری (1804), کم باری (1801)
- متوسط نرخ بازار (Average Market Rate): میان باری (2945.77), اوج باری (2945.77), کم باری (2945.77)
- حداکثر نرخ بازار عمده فروشی برق (Maximum Wholesale Market Rate): میان باری (3585.86), اوج باری (3900.71), کم باری (3186.3)
- حداکثر نرخ تابلو سبز (Maximum Green Board Rate): میان باری (80000), اوج باری (80000), کم باری (80000)
- نرخ تابلو سبز (Green Board Rate): میان باری (56758), اوج باری (56758), کم باری (56758)

## Implementation Notes

1. Each restructuring script follows the existing pattern:

- `convert_persian_digits()` for number normalization
- `parse_decimal_number()` or `parse_number()` for parsing values
- Main function that reads JSON, parses text/tables, returns structured dict
- Save to `{base_name}_restructured.json`

2. The classifier already has a `template_7.json` signature file, so detection should work automatically.

3. All 9 sections are unique to template_7 layout, hence new scripts for each.

4. **Coordinate Determination**: Before implementation, coordinates must be determined by:

- Using `analyze_pdf_coordinates.py` or similar tool on `template_7/7.pdf`
- Or manually inspecting the PDF with coordinate extraction tools
- Adjusting estimated coordinates based on actual PDF layout

5. The energy consumption table is very complex with many nested columns - may require careful parsing of table structure from extracted text/table data.

6. The PDF has 2 pages - ensure the pipeline handles multi-page extraction correctly.

7. Some values may be negative (indicated by `-` suffix) - handle these correctly in parsing.

8. The consumption history table spans multiple periods and may be quite large - ensure coordinates capture the full table.

## Testing

Test with: `python run_complete_pipeline.py template_7/7.pdf`

Expected output: `output/7_final_pipeline.json` with all 9 sections merged.

## Dependencies

- All restructuring scripts should import from existing utilities:
- `convert_persian_digits()` from any existing template script
- `parse_number()` or `parse_decimal_number