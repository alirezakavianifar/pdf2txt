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
            "y1": 420   # Bottom edge (end after last data row)
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
