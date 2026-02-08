"""
Configuration module for PDF to text extraction pipeline.
"""
from pathlib import Path
from pydantic import BaseModel
from typing import Optional, Tuple


class CropSectionConfig(BaseModel):
    """Configuration for a single crop section."""
    name: str
    description: str
    x0: float
    y0: float
    x1: float
    y1: float


class CropConfig(BaseModel):
    """Configuration for PDF cropping."""
    # Legacy single crop config (kept for backward compatibility)
    x0: float = 5.0
    y0: float = 90.0
    x1: float = 595.0
    y1: float = 262.0
    
    # Crop sections configuration
    sections: list[dict] = [
        {
            "name": "energy_supported_section",  # بهای انرژی پشتیبانی شده
            "description": "Supported Energy Values Section (Top Table)",
            "x0": 5,   # Left edge
            "y0": 90,  # Top edge  
            "x1": 595, # Right edge (max ~595 for A4)
            "y1": 262  # Bottom edge
        },
        {
            "name": "license_expiry_section",  # تاریخ انقضا پروانه
            "description": "License Expiry Date Section",
            "x0": 30,   # Left edge (starts at date: 37.2, add margin)
            "y0": 40,   # Top edge (starts at 44.2, add margin)
            "x1": 135,  # Right edge (ends at label: 123.9, add margin)
            "y1": 65    # Bottom edge (ends at date: 57.8, add margin)
        },
        {
            "name": "power_section",  # قدرت (کیلووات)
            "description": "Power Section (Kilowatts)",
            "x0": 420,  # Left edge (start after "مشخصات کنتور" section, power section starts around "محاسبه شده:" at x0=448.7)
            "y0": 255,  # Top edge (start from "قدرت (کیلووات)" header, exclude earlier content)
            "x1": 590,  # Right edge (values like "2500" end around 560-570)
            "y1": 320   # Bottom edge (last label "تاریخ اتمام کاهش موقت" ends around 318)
        },
        {
            "name": "period_section",  # اطلاعات دوره (از تاریخ، تا تاریخ، تعداد روز دوره)
            "description": "Period Information Section (From Date, To Date, Number of Days)",
            "x0": 125,  # Left edge (include full date year first digit - ensure complete date visibility)
            "y0": 255,  # Top edge (matches power section top, "از تاریخ" appears around y0=259.8)
            "x1": 265,  # Right edge (crop more from right - tighten around period information)
            "y1": 285   # Bottom edge (crop from bottom less - include "تعداد روز دوره" line)
        },
        {
            "name": "consumption_history_section",  # سوابق مصرف و مبلغ
            "description": "Consumption and Amount History Section (Table with dates and amounts)",
            "x0": 265,  # Left edge (tiny crop more from left - exclude last 3 columns from left)
            "y0": 330,  # Top edge (start above table headers)
            "x1": 595,  # Right edge (full width table)
            "y1": 440   # Bottom edge (enlarged from 420 for layout variation; includes کم باری row)
        },
        {
            "name": "bill_summary_section",  # خلاصه صورتحساب (بهای انرژی، آبونمان، مالیات، ...)
            "description": "Bill Summary Section (Energy Cost, Subscription, Tax, Total)",
            "x0": 15,   # Left edge (Values column)
            "y0": 255,  # Top edge (Starts at "بهای انرژی")
            "x1": 130,  # Right edge (End of Labels column)
            "y1": 405   # Bottom edge (Ends at "کسر هزار ریال")
        },
        {
            "name": "transit_section",  # ترانزیت (قدرت مشمول، نرخ ماهیانه، ...)
            "description": "Transit Section (Transit Power, Rate, Cost, etc.)",
            "x0": 5,
            "y0": 660,
            "x1": 260,
            "y1": 745
        },
        {
            "name": "bill_identifier_section",  # شناسه قبض
            "description": "Bill Identifier Section (Shenase Ghabz)",
            "x0": 5,
            "y0": 505,
            "x1": 130,
            "y1": 525
        },
    ]

    # Crop sections configuration for Template 2
    # NOTE: These are placeholders. You should update coordinates based on actual template_2 layout.
    sections_template_2: list[dict] = [
        {
            "name": "bill_identifier_section", 
            "description": "Bill Identifier Section (Shenase Ghabz) - Template 2",
            "x0": 20, # Text starts at 37
            "y0": 55, # Text starts at 64
            "x1": 180, # Tightened from 220 (Text ends around 172)
            "y1": 80  # Tightened from 85
        },
        {
            "name": "license_expiry_section",
            "description": "License Expiry Date Section - Template 2",
            "x0": 340, # Start left of date (357)
            "y0": 110, # Start above date (117)
            "x1": 550, # Tightened from 580
            "y1": 130  # Tightened from 135
        },
        {
            "name": "energy_supported_section",
            "description": "Supported Energy / Consumption Table - Template 2",
            "x0": 10, 
            "y0": 165, # Moved down further from 160
            "x1": 830, 
            "y1": 260 # Move Up (exclude power section below)
        },
        {
            "name": "power_section",
            "description": "Power Section (Kilowatts) - Template 2",
            "x0": 240, # Left edge of TOU column
            "y0": 355, # Top edge of Header
            "x1": 580, # Right edge of Description column (Bari/Mian Bari at x570)
            "y1": 425  # Bottom edge of last row (Ouj Bar at y417)
        },
        {
            "name": "period_section",
            "description": "Period Information - Template 2",
            "x0": 235, # Micro-adjustment from 230
            "y0": 280, 
            "x1": 418, # Micro-adjustment from 420
            "y1": 315
        },
        {
            "name": "bill_summary_section",
            "description": "Bill Financial Summary - Template 2",
            "x0": 30, 
            "y0": 280, 
            "x1": 240, # Micro-adjustment: Tightened slightly from 250
            "y1": 390  # Increased from 375 to include even more content at bottom
        },
        {
            "name": "consumption_history_section",
            "description": "Consumption History Table - Template 2",
            "x0": 230, # Back off slightly left (include start of header at 239)
            "y0": 460, 
            "x1": 825, # Extend slightly right (include end of header at 821)
            "y1": 560
        },
        {
            "name": "ghodrat_kilowatt_section",
            "description": "Power - Kilowatts Table - Template 2",
            "x0": 600, # Tightened left (exclude Zarib, start at 900)
            "y0": 275, # Moved up to include header 'Ghodrat - Kilowatt'
            "x1": 830, 
            "y1": 355
        }
    ]

    # Crop sections configuration for Template 3
    sections_template_3: list[dict] = [
        {
            "name": "bill_identifier_section",
            "description": "Bill Identifier Section (شناسه قبض) - Template 3",
            "x0": 5,
            "y0": 35,
            "x1": 160,
            "y1": 55
        },
        {
            "name": "license_expiry_section",
            "description": "License Expiry Date (تاریخ انقضا پروانه) - Template 3",
            "x0": 60,
            "y0": 80,
            "x1": 160,
            "y1": 100
        },
        {
            "name": "energy_consumption_table_section",
            "description": "Energy Consumption Table (جدول مصارف انرژی) - Template 3",
            "x0": 5,
            "y0": 125,
            "x1": 590,
            "y1": 230
        },
        {
            "name": "power_section",
            "description": "Power Section (قدرت - کیلووات) - Template 3",
            "x0": 345,
            "y0": 225,
            "x1": 590,
            "y1": 280
        },
        {
            "name": "period_section",
            "description": "Period Information (اطلاعات دوره) - Template 3",
            "x0": 445,
            "y0": 275,
            "x1": 590,
            "y1": 310
        },
        {
            "name": "reactive_consumption_section",
            "description": "Reactive Consumption (مصرف راکتیو) - Template 3",
            "x0": 260,
            "y0": 275,
            "x1": 370,
            "y1": 310
        },
        {
            "name": "bill_summary_section",
            "description": "Bill Summary (خلاصه صورتحساب) - Template 3",
            "x0": 5,
            "y0": 230,
            "x1": 155,
            "y1": 430
        },
        {
            "name": "rate_difference_table_section",
            "description": "Rate Difference Table (شرح مصارف و مابه التفاوت) - Template 3",
            "x0": 148,
            "y0": 315,
            "x1": 580,
            "y1": 400
        },
        {
            "name": "transit_section",
            "description": "Transit Section (ترانزیت) - Template 3",
            "x0": 430,
            "y0": 590,
            "x1": 590,
            "y1": 690
        }
    ]

    # Crop sections configuration for Template 4
    sections_template_4: list[dict] = [
        {
            "name": "power_section",
            "description": "Power Section (قدرت - کیلووات) - Template 4",
            "x0": 425,
            "y0": 15,
            "x1": 595,
            "y1": 62
        },
        {
            "name": "license_expiry_section",
            "description": "License Expiry Date (تاریخ انقضا پروانه) - Template 4",
            "x0": 5,
            "y0": 55,
            "x1": 145,
            "y1": 75
        },
        {
            "name": "transformer_coefficient_section",
            "description": "Transformer Coefficient (ضریب ترانس) - Template 4",
            "x0": 500,
            "y0": 95,
            "x1": 595,
            "y1": 115
        },
        {
            "name": "consumption_table_section",
            "description": "Consumption Table (شرح مصارف) - Template 4",
            "x0": 5,
            "y0": 115,
            "x1": 425,
            "y1": 215
        },
        {
            "name": "period_section",
            "description": "Period Information (اطلاعات دوره) - Template 4",
            "x0": 430,
            "y0": 120,
            "x1": 595,
            "y1": 185
        },
        {
            "name": "financial_table_section",
            "description": "Financial/Energy Cost Table (بهای انرژی) - Template 4",
            "x0": 5,
            "y0": 215,
            "x1": 595,
            "y1": 300
        },
        {
            "name": "consumption_history_section",
            "description": "Consumption History (سوابق مصارف) - Template 4",
            "x0": 260,
            "y0": 320,
            "x1": 595,
            "y1": 450
        },
        {
            "name": "bill_identifier_section",
            "description": "Bill Identifier (شناسه قبض) - Template 4",
            "x0": 400,
            "y0": 505,
            "x1": 580,
            "y1": 525
        },
        {
            "name": "transit_section",
            "description": "Transit Section (ترانزیت) - Template 4",
            "x0": 5,
            "y0": 640,
            "x1": 280,
            "y1": 750
        }
    ]

    # Crop sections configuration for Template 5
    sections_template_5: list[dict] = [
        {
            "name": "company_info_section",
            "description": "Company info & National ID (شناسه ملی) - Template 5",
            "x0": 5,
            "y0": 5,
            "x1": 300,
            "y1": 50
        },
        {
            "name": "license_expiry_section",
            "description": "License Expiry Date (تاریخ انقضای پروانه) - Template 5",
            "x0": 120,  # Less from the left (smaller x0, crops less)
            "y0": 100,
            "x1": 260,  # More from the right (larger x1, crops more)
            "y1": 130
        },
        {
            "name": "energy_consumption_table_section",
            "description": "Energy Consumption Table (جدول مصارف انرژی) - Template 5",
            "x0": 5,
            "y0": 75,
            "x1": 590,
            "y1": 250
        },
        {
            "name": "power_section",
            "description": "Power Section (قدرت - کیلووات) - Template 5",
            "x0": 370,
            "y0": 235,
            "x1": 590,
            "y1": 350
        },
        {
            "name": "period_year_section",
            "description": "Period/Year (دوره/سال) - Template 5",
            "x0": 180,  # Crop less from left to include more content
            "y0": 330,  # Crop more from above to focus on دوره/سال row only
            "x1": 400,  # Right edge to capture the period/year value
            "y1": 355   # Crop less from bottom to include more of the row
        },
        {
            "name": "period_section",
            "description": "Period Information (اطلاعات دوره) - Template 5",
            "x0": 410,  # Crop more from left to focus on period dates
            "y0": 350,  # Below power section (power ends at y1: 350)
            "x1": 590,  # Right edge to capture full horizontal date box
            "y1": 380   # Compact height for horizontal date information
        },
        {
            "name": "reactive_consumption_section",
            "description": "Reactive Consumption (مصرف راکتیو) - Template 5",
            "x0": 5,    # Start from left edge to capture full horizontal section
            "y0": 235,  # Start higher to capture مصرف راکتیو row above مبلغ راکتیو
            "x1": 365,  # Extend to before power section (starts at x0: 370)
            "y1": 280   # Extend down to capture both مصرف and مبلغ راکتیو rows
        },
        {
            "name": "bill_summary_section",
            "description": "Bill Summary (خلاصه صورتحساب) - Template 5",
            "x0": 5,
            "y0": 250,
            "x1": 200,
            "y1": 490
        },
        {
            "name": "rate_difference_table_section",
            "description": "Rate Difference Table (مشمول ما بالتفاوت اجرای مقررات) - Template 5",
            "x0": 200,
            "y0": 300,
            "x1": 590,
            "y1": 400
        },
        {
            "name": "transit_section",
            "description": "Transit Section (ترانزیت) - Template 5",
            # Crop around the transit table showing "بهای ترانزیت" with value "637,743,948"
            # The transit section is a simple 2-column table: value (left) and "بهای ترانزیت" label (right)
            # Based on the image showing consumption table being captured, transit is likely positioned differently
            # Try positioning on left side or different vertical position to avoid consumption table overlap
            "x0": 5,    # Start from left edge - transit might be on left side of page
            "y0": 500,  # Position below rate_difference_table_section
            "x1": 260,  # Extend to include both value and label columns
            "y1": 560   # Include the transit row
        },
        {
            "name": "consumption_history_section",
            "description": "Consumption History (سوابق مصارف مبالغ و پرداختهای ادوار گذشته) - Template 5",
            "x0": 200,  # Cropped more from the left to exclude last 3 columns (تاریخ پرداخت, مبلغ پرداختی, مهلت پرداخت)
            "y0": 565,  # Cropped more from above (was 400)
            "x1": 590,
            "y1": 750
        }
    ]

    # Crop sections configuration for Template 6
    sections_template_6: list[dict] = [
        {
            "name": "license_expiry_section",
            "description": "License Expiry Date (تاریخ انقضای پروانه) - Template 6",
            "x0": 280,   # Expanded left to capture more area
            "y0": 85,    # Moved up to capture license dates that appear higher (from 110 to 85)
            "x1": 500,   # Keep right boundary
            "y1": 150    # Keep bottom boundary to capture dates in both positions
        },
        {
            "name": "energy_consumption_table_section",
            "description": "Energy Consumption Table (جدول مصارف انرژی) - Template 6",
            "x0": 5,
            "y0":138,   # Cropping even more from above (increased from 90 to 100)
            "x1": 590,
            "y1": 280   # Cropping less from bottom (reduced from 250 to 230)
        },
        {
            "name": "power_section",
            "description": "Power Section (قدرت - کیلووات) - Template 6",
            "x0": 390,  # Slightly expanded left to capture full table
            "y0": 265,  # Moved up significantly to capture table header and top rows (from 310 to 265)
            "x1": 590,  # Right edge
            "y1": 550   # Keep expanded bottom to capture power tables that appear lower
        },
        {
            "name": "period_section",
            "description": "Period Information (اطلاعات دوره) - Template 6",
            "x0": 0,     # No cropping from the left
            "y0": 235,   # Moved up to capture period info that appears higher (from 280 to 235)
            "x1": 590,   # No cropping from the right (full width)
            "y1": 310    # Keep bottom boundary to capture dates in both positions
        },
        {
            "name": "bill_summary_section",
            "description": "Bill Summary (خلاصه صورتحساب) - Template 6",
            # Crop from above and bottom less to include more content vertically
            "x0": 5,    # Keep left aligned with value column
            "y0": 250,  # Crop less from the top (was 310)
            "x1": 170,  # Crop further from the right to stay within the bill-summary columns
            "y1": 680   # Crop even less from the bottom (was 660)
        },
        {
            "name": "transit_section",
            "description": "Transit Section (صورتحساب ترانزیت) - Template 6",
            "x0": 170,   # Cropped more from the left
            "y0": 450,   # Cropped LESS from above
            "x1": 380,   # Cropped EVEN MORE from the right
            "y1": 590    # Cropped LESS from the bottom to include even more
        },
        {
            "name": "consumption_history_section",
            "description": "مبالغ قابل پرداخت (Amounts Payable) - Template 6 (Expanded Upwards)",
            "x0": 5,     # Full width
            "y0": 560,   # Expanded further upwards to include more rows/band
            "x1": 590,
            "y1": 640
        }
    ]

    # Crop sections configuration for Template 7
    sections_template_7: list[dict] = [
        {
            "name": "bill_identifier_section",
            "description": "Bill Identifier (شناسه قبض) - Template 7",
            "x0": 5,
            "y0": 5,
            "x1": 180,  # Cropped more from right (was 280)
            "y1": 45  # Cropped less from bottom (was 35)
        },
        {
            "name": "license_expiry_section",
            "description": "License Expiry Date (تاریخ انقضا پروانه) - Template 7",
            "x0": 5,
            "y0": 30,
            "x1": 200,
            "y1": 55
        },
        {
            "name": "company_info_section",
            "description": "Company Information - Template 7",
            "x0": 5,
            "y0": 5,
            "x1": 400,
            "y1": 80
        },
        {
            "name": "energy_consumption_table_section",
            "description": "Energy Consumption Table (جدول مصارف انرژی) - Template 7",
            "x0": 5,
            "y0": 80,
            "x1": 590,
            "y1": 280
        },
        {
            "name": "power_section",
            "description": "Power Section (قدرت - کیلووات) - Template 7",
            "x0": 400,
            "y0": 280,
            "x1": 590,
            "y1": 350
        },
        {
            "name": "period_section",
            "description": "Period Information (اطلاعات دوره) - Template 7",
            "x0": 400,
            "y0": 350,
            "x1": 590,
            "y1": 380
        },
        {
            "name": "bill_summary_section",
            "description": "Bill Summary (خلاصه صورتحساب) - Template 7",
            "x0": 5,
            "y0": 260,
            "x1": 400,
            "y1": 450
        },
        {
            "name": "consumption_history_section",
            "description": "Consumption History (سوابق مصرف، مبالغ و پرداخت های دوره های گذشته) - Template 7",
            "x0": 20,   # Start from left with small margin to include green border
            "y0": 550,  # Start right at table header (tight crop to minimize content above)
            "x1": 595,  # Full width table (within PDF bounds)
            "y1": 580   # End right after last data row (tight crop to minimize content below)
        },
        {
            "name": "transit_section",
            "description": "Transit Section (ترانزیت) - Template 7",
            "x0": 400,
            "y0": 450,
            "x1": 590,
            "y1": 550
        }
    ]

    # Crop sections configuration for Template 8
    sections_template_8: list[dict] = [
        {
            "name": "bill_identifier_section",
            "description": "Bill Identifier Section (شناسه قبض) - Template 8",
            "x0": 380,
            "y0": 655,
            "x1": 585,
            "y1": 685
        },
        {
            "name": "license_expiry_section",
            "description": "License Expiry Date (تاریخ انقضا پروانه) - Template 8",
            # Based on measured coordinates in template_8/8.pdf:
            #   - Date '1425/01/01' at approx x0=50, y0=46.2, x1=83.3, y1=59.7
            #   - Label text to the right up to ~x1=141.5
            # We add a small margin around these bounds.
            "x0": 45,   # Slightly left of the date
            "y0": 40,   # Above the date/label line
            "x1": 150,  # Right of the label text
            "y1": 70    # Below the date/label line
        },
        {
            "name": "energy_consumption_table_section",
            "description": "Energy Consumption Table (جدول مصارف انرژی) - Template 8",
            "x0": 5,
            "y0": 100,
            "x1": 590,
            "y1": 350
        },
        {
            "name": "power_section",
            "description": "Power Section (قدرت - کیلووات) - Template 8",
            "x0": 350,
            "y0": 430,
            "x1": 580,
            "y1": 470
        },
        {
            "name": "period_section",
            "description": "Period Information (اطلاعات دوره) - Template 8",
            "x0": 280,
            "y0": 430,
            "x1": 400,
            "y1": 450
        },
        {
            "name": "consumption_history_section",
            "description": "Consumption History (سوابق مصارف، مبالغ و پرداختهای دوره های گذشته) - Template 8",
            # Crop in further from the left and top to tighten around the table
            "x0": 170,  # Crop further from the left
            "y0": 490,
            "x1": 590,
            "y1": 600
        },
        {
            "name": "bill_summary_section",
            "description": "Bill Summary (خلاصه صورتحساب) - Template 8",
            "x0": 30,
            "y0": 430,
            "x1": 200,
            "y1": 605
        },
        {
            "name": "transit_section",
            "description": "Transit Section (ترانزیت) - Template 8",
            # Tight crop around the bottom-left transit financial box:
            #   - Values like "592,454,938" start around x≈46, y≈710
            #   - Labels like "بهای ترانزیت برق" extend to about x≈162, y≈785
            #   - We exclude the footer line at y≈811 (contact info)
            "x0": 40,   # Slightly left of the first value column
            "y0": 690,  # Crop less from above; move crop up to include even more area above
            "x1": 180,  # Right of the longest label text
            "y1": 790   # Just below the "مبلغ قابل پرداخت" row, above footer
        }
    ]

    # Crop sections configuration for Template 9
    sections_template_9: list[dict] = [
        {
            "name": "bill_identifier_section",
            "description": "Bill Identifier Section (شناسه قبض) - Template 9",
            "x0": 20,   # Left edge
            "y0": 20,   # Top edge (moved up by 35 units, i.e., up from 55 to 20)
            "x1": 185,  # Right edge (cropped in further from right to exclude more, reduced from 200)
            "y1": 60    # Bottom edge (expanded further down from 45 to 60)
        },
        {
            "name": "license_expiry_section",
            "description": "License Expiry Date Section (تاریخ انقضای پروانه) - Template 9",
            "x0": 340,  # Left edge
            "y0": 110,  # Top edge
            "x1": 550,  # Right edge
            "y1": 130   # Bottom edge
        },
        {
            "name": "consumption_table_section",
            "description": "Consumption Table (جدول مصارف) - Template 9",
            "x0": 8,    # Slightly expanded left, allow wider margin
            "y0": 120,  # Expanded upward to include potential header overflow
            "x1": 410,  # Slightly expanded right, max page width ~595
            "y1":235   # Expanded downward for multi-row table or footer lines
        },
        {
            "name": "period_section",
            "description": "Period Information Section (اطلاعات دوره) - Template 9",
            "x0": 180,   # Left edge (tightened even further to exclude more fields on the left)
            "y0": 220,   # Top edge (unchanged)
            "x1": 420,   # Right edge (tightened even further to exclude more fields on the right)
            "y1": 335    # Bottom edge (unchanged)
        },
        {
            "name": "power_section",
            "description": "Power Section (قدرت - کیلووات) - Template 9",
            "x0": 400,   # Expanded further left to include additional area
            "y0": 140,   # Expanded further up to capture more area above
            "x1": 620,   # Expanded further right to include more area
            "y1": 235   # Tightened bottom edge to exclude even more from below
        },
        {
            "name": "bill_summary_section",
            "description": "Bill Summary Section (خلاصه صورتحساب) - Template 9",
            "x0": 5,    # Left edge
            "y0": 290,  # Top edge (expanded upward by 10 more units from 320 to 310)
            "x1": 210,  # Right edge
            "y1": 460   # Bottom edge (unchanged, leaving at 460 so only the top moves up)
        },
        {
            "name": "consumption_history_section",
            "description": "Consumption History Table (سوابق مصارف) - Template 9",
            "x0": 5,    # Left edge
            "y0": 480,  # Top edge
            "x1": 590,  # Right edge (wide table, max page width ~595)
            "y1": 650   # Bottom edge expanded further down from 600 to 630
        }
    ]


class ExtractionConfig(BaseModel):
    """Configuration for text extraction."""
    use_ocr: bool = False  # Use OCR if text extraction fails
    ocr_lang: str = "fas+eng"  # Persian + English
    preserve_layout: bool = True
    extract_tables: bool = True
    table_strategy: str = "lines"  # "lines", "text", "explicit"


class NormalizationConfig(BaseModel):
    """Configuration for text normalization."""
    normalize_whitespace: bool = True
    remove_extra_spaces: bool = True
    normalize_persian_numbers: bool = True
    handle_bidi: bool = True  # Apply BIDI to convert visual-order to logical-order text


class GeometryConfig(BaseModel):
    """Configuration for geometry extraction."""
    extract_cell_bounds: bool = True
    extract_table_structure: bool = True
    min_cell_width: float = 10.0
    min_cell_height: float = 10.0


class StripExtractionConfig(BaseModel):
    """Configuration for strip-based extraction."""
    row_height: float = 11.0  # Typical row height in points
    min_strip_height: float = 8.0  # Minimum strip height for last strip
    x_margin: float = 5.0  # Horizontal margin to avoid clipping text


class PDF2TextConfig(BaseModel):
    """Main configuration for PDF to text pipeline."""
    input_dir: Path = Path("template1")
    output_dir: Path = Path("output")
    crop: CropConfig = CropConfig()
    extraction: ExtractionConfig = ExtractionConfig()
    normalization: NormalizationConfig = NormalizationConfig()
    geometry: GeometryConfig = GeometryConfig()
    strip_extraction: StripExtractionConfig = StripExtractionConfig()
    
    # File patterns
    input_pattern: str = "*_cropped.pdf"  # Only process cropped PDFs
    exclude_pattern: str = "*_cropped_cropped.pdf"  # Exclude double-cropped files
    
    # Output formats
    output_formats: list[str] = ["json"]  # Only JSON output
    
    class Config:
        arbitrary_types_allowed = True


# Default configuration instance
default_config = PDF2TextConfig()
