# Script Analysis - Pipeline Components

## ✅ **CORE PIPELINE SCRIPTS** (Required - Keep)

### 1. `adjust_crop.py` ⭐ **ACTIVE**
- **Purpose:** Batch crop PDFs to table region
- **Used in pipeline:** Yes - Step 1 (cropping)
- **Status:** KEEP - Main cropping script

### 2. `extract_text.py` ⭐ **ACTIVE**
- **Purpose:** Main text and table extraction pipeline
- **Used in pipeline:** Yes - Step 2 (extraction)
- **Imports:** `config`, `text_normalization`, `geometry_extraction`
- **Status:** KEEP - Core pipeline script

### 3. `config.py` ⭐ **ACTIVE**
- **Purpose:** Configuration management (Pydantic models)
- **Used in pipeline:** Yes - Imported by `extract_text.py`
- **Status:** KEEP - Required dependency

### 4. `text_normalization.py` ⭐ **ACTIVE**
- **Purpose:** Text cleaning, Persian digit conversion, BIDI handling
- **Used in pipeline:** Yes - Imported by `extract_text.py`
- **Status:** KEEP - Required dependency

### 5. `geometry_extraction.py` ⭐ **ACTIVE**
- **Purpose:** Table structure and cell boundary extraction
- **Used in pipeline:** Yes - Imported by `extract_text.py`
- **Status:** KEEP - Required dependency

---

## ❌ **REDUNDANT SCRIPTS** (Remove)

### 6. `apply_crop.py` ❌ **REDUNDANT**
- **Purpose:** Single PDF crop utility
- **Redundant because:** `adjust_crop.py` does batch cropping with same functionality
- **Status:** DELETE - Functionality covered by `adjust_crop.py`

### 7. `crop_table_from_image.py` ❌ **REDUNDANT**
- **Purpose:** One-time crop script for specific coordinates
- **Redundant because:** `adjust_crop.py` handles this with configurable coordinates
- **Status:** DELETE - One-time utility, no longer needed

### 8. `find_and_crop_table.py` ❌ **REDUNDANT**
- **Purpose:** Combines finding bounding box and cropping
- **Redundant because:** 
  - We use fixed coordinates from visual analysis
  - `adjust_crop.py` handles cropping
  - Not used in main pipeline
- **Status:** DELETE - Superseded by `adjust_crop.py`

### 9. `find_table_bbox.py` ❌ **REDUNDANT**
- **Purpose:** Programmatically find table bounding box
- **Redundant because:**
  - We use fixed coordinates (determined visually)
  - Not used in main pipeline
  - Utility script only
- **Status:** DELETE - Not used in pipeline

### 10. `create_grid_overlay.py` ❌ **REDUNDANT**
- **Purpose:** Create grid overlay for manual coordinate finding
- **Redundant because:**
  - Coordinates already determined
  - One-time utility, not part of pipeline
- **Status:** DELETE - One-time utility, no longer needed

---

## 🧪 **TEST/DEBUG SCRIPTS** (Remove)

### 11. `test_ocr.py` ❌ **TEST SCRIPT**
- **Purpose:** Test OCR extraction
- **Status:** DELETE - Test script, not part of pipeline

### 12. `test_ocr_improved.py` ❌ **TEST SCRIPT**
- **Purpose:** Improved OCR testing
- **Status:** DELETE - Test script, not part of pipeline

### 13. `test_extraction.py` ❌ **TEST SCRIPT**
- **Purpose:** Test extraction methods
- **Status:** DELETE - Test script, not part of pipeline

### 14. `check_pdf_type.py` ❌ **DEBUG SCRIPT**
- **Purpose:** Check if PDF is text-based or image-based
- **Status:** DELETE - Debug utility, not part of pipeline

### 15. `check_ocr_output.py` ❌ **DEBUG SCRIPT**
- **Purpose:** Check OCR output quality
- **Status:** DELETE - Debug utility, not part of pipeline

---

## 📊 Summary

### **Scripts to KEEP (5):**
1. `adjust_crop.py` - Main cropping
2. `extract_text.py` - Main extraction
3. `config.py` - Configuration
4. `text_normalization.py` - Text normalization
5. `geometry_extraction.py` - Geometry extraction

### **Scripts to DELETE (10):**
1. `apply_crop.py` - Redundant
2. `crop_table_from_image.py` - Redundant
3. `find_and_crop_table.py` - Redundant
4. `find_table_bbox.py` - Redundant
5. `create_grid_overlay.py` - Redundant
6. `test_ocr.py` - Test script
7. `test_ocr_improved.py` - Test script
8. `test_extraction.py` - Test script
9. `check_pdf_type.py` - Debug script
10. `check_ocr_output.py` - Debug script

---

## 🔄 Final Pipeline Structure

```
Core Pipeline:
├── adjust_crop.py          (Step 1: Crop PDFs)
└── extract_text.py         (Step 2: Extract & Export)
    ├── config.py           (Configuration)
    ├── text_normalization.py (Text processing)
    └── geometry_extraction.py (Table structure)
```

**Total: 5 scripts** (down from 15)
