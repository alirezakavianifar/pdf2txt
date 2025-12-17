# Template 8 Extraction Pipeline Implementation

## Overview

Template 8 PDFs have a distinct layout with 8 sections that need extraction. Based on analysis of `template_8/8.pdf` and the provided images, the following sections have been identified with their coordinates.

## Section Coordinates (Template 8)

Based on the images provided, template_8 has the following sections. **Note:** Exact coordinates need to be determined by analyzing the PDF layout, but approximate positions are estimated below:

| Section | Description | Estimated Coordinates (x0, y0, x1, y1) | Notes |

|---------|-------------|----------------------------------------|-------|

| `bill_identifier_section` | شناسه قبض | (5, 35, 160, 70) | Green box with bill ID like "220.752540.3220" |

| `license_expiry_section` | تاریخ انقضا پروانه | (5, 70, 160, 95) | Green box with date like "1425/01/01" |

| `energy_consumption_table_section` | جدول مصارف انرژی | (5, 100, 590, 350) | Complex multi-section table with multiple subsections |

| `power_section` | قدرت (کیلووات) | (400, 350, 590, 420) | Power values: contractual, calculated, allowed, reduced, consumed, overage |

| `period_section` | اطلاعات دوره | (400, 420, 590, 460) | From/to dates and number of days |

| `consumption_history_section` | سوابق مصارف، مبالغ و پرداختهای دوره های گذشته | (5, 460, 590, 600) | Historical consumption table with 6+ periods |

| `bill_summary_section` | خلاصه صورتحساب | (5, 600, 300, 750) | Financial summary items |

| `transit_section` | ترانزیت | (300, 600, 590, 750) | Transit costs and related charges |

**Important:** The exact coordinates above are estimates and need to be verified by:

1. Opening `template_8/8.pdf` in a PDF viewer
2. Measuring the exact pixel/point coordinates of each section
3. Adjusting the coordinates in `config.py`

## Files to Modify

### 1. [config.py](config.py) - Add template_8 sections

Add a new `sections_template_8` list with the 8 section coordinates. The structure should follow the pattern used for `sections_template_3`:

```python
sections_template_8: list[dict] = [
    {
        "name": "bill_identifier_section",
        "description": "Bill Identifier Section (شناسه قبض) - Template 8",
        "x0": 5,
        "y0": 35,
        "x1": 160,
        "y1": 70
    },
    # ... other sections
]
```

### 2. [run_complete_pipeline.py](run_complete_pipeline.py) - Add template_8 processing

Add a new `process_template_8()` function similar to `process_template_3()`, and update the main branching logic to handle `template_8`:

```python
elif template_id in ["template_8", "template8"]:
    process_template_8(input_pdf, output_dir, template_id, confidence)
```

## New Scripts to Create

### 3. `restructure_bill_identifier_template8.py`

Extract bill identifier (شناسه قبض) from the green-bordered box.

**Expected format:** Value like `220.752540.3220` (may contain dots as separators)

**Extraction logic:**

- Look for text in green-bordered section
- Extract numeric identifier (may contain dots)
- Normalize Persian/Arabic-Indic digits
- Return as string (preserve dot separators if present)

**Output structure:**

```json
{
  "bill_identifier_section": {
    "bill_id": "220.752540.3220"
  }
}
```

### 4. `restructure_license_expiry_template8.py`

Extract license expiry date (تاریخ انقضای پروانه) from the green-bordered box.

**Expected format:** Date like `1425/01/01` (Persian calendar format: YYYY/MM/DD)

**Extraction logic:**

- Look for date pattern in green-bordered section
- Extract date in format YYYY/MM/DD
- Normalize Persian/Arabic-Indic digits
- Validate date format

**Output structure:**

```json
{
  "license_expiry_section": {
    "license_expiry_date": "1425/01/01"
  }
}
```

### 5. `restructure_energy_consumption_template8.py`

Parse the complex energy consumption table with multiple subsections.

**Table structure includes:**

1. **انرژی قرائت شده (Read Energy)** section with columns:

   - شرح مصارف (Consumption Description): میان باری, اوج باری, کم باری, اوج بار جمعه, راکتیو
   - شمارنده قبلی (Previous Counter)
   - شمارنده کنونی (Current Counter)
   - مصرف کل (Total Consumption)
   - مبلغ (Amount)

2. **خرید سبز (Green Purchase)** section with columns:

   - بورس (Exchange)
   - دو جانبه (Bilateral)

3. **خرید عادی (Normal Purchase)** section with columns:

   - بورس (Exchange)
   - دو جانبه (Bilateral)

4. **نرخ (Rate)** section with columns:

   - مبلغ با حداکثر نرخ بازار (Amount with Max Market Rate)
   - مبلغ با نرخ تابلو دو (Amount with Bilateral Board Rate)
   - مبلغ با نرخ تعرفه (Amount with Tariff Rate)

5. **ماده ۵ (Article 5)** section with columns:

   - حداکثر نرخ بازار (Max Market Rate)
   - نرخ تابلو دو (Bilateral Board Rate)
   - نرخ تعرفه (Tariff Rate)
   - مبلغ (Amount)
   - نرخ (Rate)
   - انرژی مشمول (Included Energy)

6. **ماده ۱۶ (Article 16)** section with columns:

   - شرح مصارف (Consumption Description)
   - انرژی مشمول (Included Energy)
   - نرخ (Rate)
   - مبلغ (Amount)

7. **سایر (Other)** section with columns:

   - مبلغ (Amount)
   - نرخ (Rate)
   - انرژی مشمول راکتیو و عوارض برق (Included Energy Reactive and Electricity Duties)

8. **بستانکاری خارج بازار (Off-market Credit)** section

9. **مابه التفاوت اجرای مقررات (Difference in Regulation Implementation)** section

10. **پشتیبانی شده توسط مالک شبکه (Supported by Network Owner)** section

**Extraction logic:**

- Parse table structure with multiple subsections
- Extract rows for each consumption type (میان باری, اوج باری, کم باری, etc.)
- Extract values for each column in each subsection
- Handle empty cells (represented as dots or empty)
- Normalize all numeric values

**Output structure:**

```json
{
  "energy_consumption_table_section": {
    "read_energy": {
      "rows": [
        {
          "description": "میان باری",
          "previous_counter": 786.68,
          "current_counter": 797.51,
          "total_consumption": 86608.0,
          "amount": 553251904
        },
        // ... other rows
      ]
    },
    "green_purchase": {
      "exchange": {},
      "bilateral": {}
    },
    "normal_purchase": {
      "exchange": {},
      "bilateral": {}
    },
    "rates": {
      "rows": [
        {
          "description": "میان باری",
          "amount_max_market_rate": 210564163,
          "amount_bilateral_rate": 6928640000,
          "amount_tariff_rate": 553251904
        },
        // ... other rows
      ]
    },
    "article_5": {
      "rows": [
        {
          "description": "میان باری",
          "tariff_rate": 6388,
          "included_energy": 50370
        },
        // ... other rows
      ]
    },
    "article_16": {
      "rows": [
        {
          "description": "میان باری",
          "included_energy": 50370
        },
        // ... other rows
      ]
    },
    "other": {
      "rows": [
        {
          "description": "میان باری",
          "amount": 403733412,
          "rate": 4661.62,
          "included_energy": 86608
        },
        // ... other rows
      ]
    },
    "off_market_credit": {},
    "regulation_difference": {
      "rows": [
        {
          "description": "میان باری",
          "amount": 298124656,
          "rate": 3442.23,
          "included_energy": 86608
        },
        // ... other rows
      ]
    },
    "network_owner_support": {
      "rows": [
        {
          "description": "میان باری",
          "included_energy": 86608,
          "rate": 4661.62,
          "amount": 403733412
        },
        // ... other rows
      ]
    }
  }
}
```

### 6. `restructure_power_section_template8.py`

Extract power values from the power section.

**Expected values:**

- قراردادی (Contractual): 5000000 (or 5000.00)
- محاسبه شده (Calculated): 4500.00
- مجاز (Permitted/Allowed): (may be empty)
- کاهش یافته (Reduced): (may be empty)
- مصرفی (Consumed): 872.00
- میزان تجاوز از قدرت (Amount of power exceeding/overage): (may be empty)

**Extraction logic:**

- Look for labels in Persian
- Extract corresponding numeric values
- Handle empty values (represented as dots)
- Normalize decimal numbers (may use slash or dot as separator)

**Output structure:**

```json
{
  "power_section": {
    "contractual_power": 5000000,
    "calculated_power": 4500.00,
    "permitted_power": null,
    "reduced_power": null,
    "consumed_power": 872.00,
    "power_overage": null
  }
}
```

### 7. `restructure_period_section_template8.py`

Extract period information.

**Expected values:**

- از تاریخ (From Date): 1404/06/01
- تا تاریخ (To Date): 1404/07/01
- تعداد روز دوره (Number of days in the period): 31
- دوره/سال (Period/Year): 1404/06 (may be present)

**Extraction logic:**

- Look for date range labels
- Extract dates in Persian calendar format (YYYY/MM/DD)
- Extract number of days
- Normalize Persian/Arabic-Indic digits

**Output structure:**

```json
{
  "period_section": {
    "from_date": "1404/06/01",
    "to_date": "1404/07/01",
    "number_of_days": 31,
    "period_year": "1404/06"
  }
}
```

### 8. `restructure_consumption_history_template8.py`

Parse the consumption history table (سوابق مصارف، مبالغ و پرداختهای دوره های گذشته).

**Table structure:**

- Columns:
  - دوره (Period): e.g., "1404/01"
  - تاریخ قرائت (Reading Date): e.g., "03/12/30"
  - میان باری (Mid-load): consumption value
  - اوج باری (Peak-load): consumption value
  - کم باری (Off-peak load): consumption value
  - اوج بار جمعه (Friday Peak-load): usually empty (dot)
  - راکتیو (Reactive): consumption value
  - مبلغ دوره (Period Amount): monetary value

**Expected data:** 6+ rows of historical periods

**Extraction logic:**

- Parse table rows
- Extract period identifier
- Extract reading date
- Extract consumption values for each load type
- Extract period amount
- Handle empty cells (Friday Peak-load often empty)

**Output structure:**

```json
{
  "consumption_history_section": {
    "historical_periods": [
      {
        "period": "1404/01",
        "reading_date": "03/12/30",
        "mid_load": 111816,
        "peak_load": 22400,
        "off_peak_load": 50704,
        "friday_peak_load": null,
        "reactive": 189120,
        "period_amount": 2833536511
      },
      {
        "period": "1404/02",
        "reading_date": "04/02/01",
        "mid_load": 79240,
        "peak_load": 16408,
        "off_peak_load": 34960,
        "friday_peak_load": null,
        "reactive": 149840,
        "period_amount": 2665134912
      },
      // ... more periods (typically 6+)
    ]
  }
}
```

### 9. `restructure_bill_summary_template8.py`

Extract financial summary items from the bill summary section.

**Expected items:**

- مبلغ مصرف (Consumption amount): 3,631,409,318
- بهای قدرت (Power price): (may be empty)
- تجاوز از قدرت (Power excess/overage): (may be empty)
- تفاوت انقضای اعتبار پروانه (Difference in license validity expiration): (may be empty)
- بهای آبونمان (Subscription fee): 143,481
- هزینه سوخت نیروگاهی (Power plant fuel cost): 99,762,920
- بهای انرژی تامین شده (Price of energy supplied): 1,074,173,969
- بهای انرژی ماده ۱۶ (Price of energy, Article 16): (may be empty)
- مابه التفاوت اجرای مقررات (Difference in regulation implementation): 932,136,460
- بستانکاری، خرید خارج بازار (Credit, off-market purchase): (may be empty)
- مابه التفاوت تأمین از تجدیدپذیر (Difference in renewable energy supply): (may be empty)
- بهای برق دوره (Electricity price for the period): 5,737,626,149
- مالیات و عوارض (Taxes and duties): 573,762,615
- عوارض برق (Electricity duties/fees): 632,993,760
- بستانکاری (Credit): -38,455,013 (may be negative)
- کسر هزار ریال (Less thousand Rials): 511

**Extraction logic:**

- Parse label-value pairs
- Extract monetary values (remove commas, normalize digits)
- Handle negative values (credit)
- Handle empty values

**Output structure:**

```json
{
  "bill_summary_section": {
    "consumption_amount": 3631409318,
    "power_price": null,
    "power_excess": null,
    "license_expiry_difference": null,
    "subscription_fee": 143481,
    "fuel_cost": 99762920,
    "supplied_energy_cost": 1074173969,
    "article_16_energy_cost": null,
    "regulation_difference": 932136460,
    "off_market_credit": null,
    "renewable_supply_difference": null,
    "period_electricity_cost": 5737626149,
    "taxes_and_duties": 573762615,
    "electricity_duties": 632993760,
    "credit": -38455013,
    "thousand_rial_deduction": 511
  }
}
```

### 10. `restructure_transit_section_template8.py`

Extract transit section data.

**Expected items:**

- بهای ترانزیت برق (Electricity Transit Price): 592,454,938
- بهای ترانزیت (Transit Price): (may be a sub-header)
- مالیات بر ارزش افزوده (Value Added Tax): 59,245,494
- بدهکاری / بستانکاری (Debit / Credit): 1,536,519,423
- کسر هزار ریال (Deduction in Thousand Rials): 855
- مبلغ قابل پرداخت (Amount Payable): 2,188,219,000

**Extraction logic:**

- Parse label-value pairs
- Extract monetary values
- Identify total/amount payable

**Output structure:**

```json
{
  "transit_section": {
    "transit_price": 592454938,
    "vat": 59245494,
    "debit_credit": 1536519423,
    "thousand_rial_deduction": 855,
    "amount_payable": 2188219000
  }
}
```

## Implementation Notes

1. **Coordinate Determination:**

   - The coordinates listed above are estimates
   - **CRITICAL:** Open `template_8/8.pdf` in a PDF viewer and measure exact coordinates
   - Use PDF coordinate system (points, where A4 is typically 595x842 points)
   - Verify coordinates by cropping test sections

2. **Common Functions:**

   - Each restructuring script should include:
     - `convert_persian_digits()` for number normalization
     - `parse_decimal_number()` or `parse_number()` for parsing values
     - Main function that reads JSON, parses text, returns structured dict

3. **Template Detection:**

   - Verify that the classifier has a `template_8.json` signature file
   - If not, create one based on unique characteristics of template_8 PDFs

4. **Text Extraction:**

   - Template 8 may have complex table structures
   - Consider using both text extraction and potentially table extraction methods
   - Handle Persian/Arabic-Indic digits throughout

5. **Empty Values:**

   - Empty cells in tables are often represented as single dots (.)
   - Handle these appropriately (set to null in JSON)

6. **Number Formatting:**

   - Numbers may use commas as thousand separators
   - Decimal numbers may use slash (/) or dot (.) as separator
   - Normalize all to standard format

## Testing

1. **Coordinate Verification:**
   ```bash
   # Test cropping with estimated coordinates
   python adjust_crop.py template_8/8.pdf <section_name> <x0> <y0> <x1> <y1>
   ```

2. **Individual Section Testing:**
   ```bash
   # Test each restructuring script individually
   python restructure_bill_identifier_template8.py output/8_bill_identifier_section.json
   ```

3. **Full Pipeline Testing:**
   ```bash
   python run_complete_pipeline.py template_8/8.pdf
   ```

4. **Expected Output:**

   - `output/8_final_pipeline.json` with all 8 sections merged
   - Verify all sections are extracted correctly
   - Check numeric values are properly normalized
   - Verify dates are in correct format

## Section Priority

For initial implementation, prioritize sections in this order:

1. **High Priority (Core Data):**

   - `bill_identifier_section` - Essential for bill identification
   - `license_expiry_section` - Important regulatory data
   - `period_section` - Critical for billing period
   - `bill_summary_section` - Core financial data

2. **Medium Priority (Detailed Data):**

   - `power_section` - Important for capacity tracking
   - `consumption_history_section` - Historical analysis
   - `transit_section` - Transit costs

3. **Lower Priority (Complex Tables):**

   - `energy_consumption_table_section` - Most complex, can be refined iteratively

## Next Steps

1. Open `template_8/8.pdf` and measure exact coordinates for each section
2. Update coordinates in `config.py`
3. Create restructuring scripts starting with high-priority sections
4. Test each section individually
5. Integrate into main pipeline
6. Test with all template_8 PDFs in the folder
7. Refine extraction logic based on test results