# PDF to Text Extraction Pipeline - How It Works

## 📋 Overview

This pipeline extracts structured text and table data from Persian/Arabic PDFs (specifically energy consumption bills). It handles right-to-left (RTL) text, normalizes Persian digits, and outputs clean JSON files.

---

## 🔄 Complete Pipeline Flow

```
Original PDFs → Crop → Extract → Normalize → Export JSON
```

### Step-by-Step Process:

```
1. PDF Cropping (adjust_crop.py)
   ↓
2. Text Extraction (extract_text.py)
   ↓
3. Text Normalization (text_normalization.py)
   ↓
4. Table Extraction & Geometry (geometry_extraction.py)
   ↓
5. JSON Export
```

---

## 📝 Detailed Pipeline Steps

### **Step 1: PDF Cropping** (`adjust_crop.py`)

**Purpose:** Crop PDFs to focus only on the table region, removing headers, footers, and margins.

**How it works:**
1. **Input:** Original PDF files in `template1/` directory
2. **Process:**
   - Opens each PDF using PyMuPDF (fitz)
   - Applies crop box coordinates: `(x0=5, y0=90, x1=595, y1=262)` in PDF points
   - Sets the crop box on the first page
   - Saves as `*_cropped.pdf` in the same directory
3. **Output:** Cropped PDFs containing only the table region

**Key Code:**
```python
crop = fitz.Rect(x0, y0, x1, y1)  # Define crop rectangle
page.set_cropbox(crop)            # Apply crop
doc.save(output_pdf)              # Save cropped PDF
```

**Why crop first?**
- Reduces noise from headers/footers
- Focuses extraction on relevant data
- Improves table detection accuracy

---

### **Step 2: Text Extraction** (`extract_text.py` - `extract_text()`)

**Purpose:** Extract raw text from cropped PDF pages.

**How it works:**
1. **Uses pdfplumber** to open and read PDF
2. **Extracts text** from the first page:
   ```python
   page = pdf.pages[0]
   text = page.extract_text()
   ```
3. **Fallback:** If extraction fails, tries with `layout=True` to preserve layout
4. **Output:** Raw text string (may be in visual order for RTL languages)

**What gets extracted:**
- All visible text from the page
- Preserves line breaks and spacing
- Handles mixed Persian/English text

---

### **Step 3: Text Normalization** (`text_normalization.py`)

**Purpose:** Clean and normalize extracted text, especially for RTL languages.

**How it works:**

#### 3.1 Whitespace Normalization
- Converts `\r\n` → `\n` (standardize line endings)
- Removes multiple consecutive spaces
- Cleans up spaces around line breaks

#### 3.2 Persian/Arabic Digit Conversion
- Converts Persian digits (۰۱۲۳...) → ASCII (0123...)
- Converts Arabic digits (٠١٢٣...) → ASCII (0123...)
- Example: `۱۴۰۴` → `1404`

#### 3.3 BIDI (Bidirectional Text) Processing ⭐ **Critical Step**
- **Problem:** PDFs store RTL text in **visual order** (as displayed)
- **Solution:** Apply BIDI algorithm to convert to **logical order** (readable order)
- Uses `python-bidi` library's `get_display()` function
- **Without BIDI:** Text appears garbled: `:ﺐﺼﻧ ﺦﯾﺭﺎﺗ`
- **With BIDI:** Text is readable: `تاریخ نصب:`

**Key Code:**
```python
from bidi.algorithm import get_display
bidi_text = get_display(text)  # Converts visual → logical order
```

**Why this matters:**
- Persian/Arabic text in PDFs is stored backwards (visual order)
- BIDI algorithm reverses it to proper reading order
- Essential for correct text storage in JSON

---

### **Step 4: Table Extraction** (`extract_text.py` - `extract_table()`)

**Purpose:** Extract structured table data from PDF.

**How it works:**
1. **Detects tables** using pdfplumber's `extract_tables()`
2. **Processes each cell:**
   - Converts cell content to string
   - Normalizes text (whitespace, digits, BIDI)
   - Handles empty cells
3. **Creates DataFrame:**
   - First row becomes headers
   - Remaining rows become data
   - Handles duplicate column names (adds `_1`, `_2`, etc.)
4. **Output:** pandas DataFrame with clean table data

**Example:**
```python
tables = page.extract_tables()  # Find tables
table = tables[0]               # Use first table
# Normalize each cell
normalized_table = [[normalize(cell) for cell in row] for row in table]
df = pd.DataFrame(normalized_table[1:], columns=normalized_table[0])
```

---

### **Step 5: Geometry Extraction** (`geometry_extraction.py`)

**Purpose:** Extract table structure and cell boundaries (optional).

**How it works:**
1. **Extracts table geometry** using pdfplumber
2. **Calculates cell positions:**
   - Row/column indices
   - Bounding boxes (x0, y0, x1, y1) for each cell
   - Table dimensions
3. **Output:** `TableGeometry` object with:
   - Number of rows/columns
   - Cell boundaries
   - Table bounding box

**Used for:**
- Understanding table structure
- Cell-level data extraction
- Layout analysis

---

### **Step 6: JSON Export** (`extract_text.py` - `save_results()`)

**Purpose:** Combine all extracted data into a clean JSON file.

**How it works:**
1. **Builds JSON structure:**
   ```json
   {
     "source_file": "1_cropped.pdf",
     "text": "normalized text...",
     "table": {
       "headers": ["col1", "col2", ...],
       "rows": [[row1_data], [row2_data], ...],
       "row_count": 76,
       "column_count": 34
     },
     "table_info": {
       "rows": 76,
       "columns": 34
     }
   }
   ```

2. **Saves to file:**
   - UTF-8 encoding
   - Pretty-printed (indented)
   - `ensure_ascii=False` to preserve Persian characters

3. **Output:** One JSON file per cropped PDF in `output/` directory

---

## 🔧 Configuration System (`config.py`)

**Purpose:** Centralized configuration using Pydantic models.

**Key Settings:**

### Crop Configuration
```python
CropConfig(
    x0=5.0,   # Left edge
    y0=90.0,  # Top edge
    x1=595.0, # Right edge
    y1=262.0  # Bottom edge
)
```

### Extraction Configuration
```python
ExtractionConfig(
    extract_tables=True,      # Extract table data
    preserve_layout=True,     # Preserve text layout
    use_ocr=False            # OCR fallback (not used)
)
```

### Normalization Configuration
```python
NormalizationConfig(
    normalize_whitespace=True,      # Clean whitespace
    normalize_persian_numbers=True, # Convert ۰۱۲ → 012
    handle_bidi=True               # Fix RTL text order
)
```

---

## 🚀 Execution Flow

### Running the Pipeline:

1. **Crop PDFs:**
   ```bash
   python adjust_crop.py
   ```
   - Processes all `*.pdf` files in `template1/`
   - Creates `*_cropped.pdf` files

2. **Extract Text:**
   ```bash
   python extract_text.py
   ```
   - Processes all `*_cropped.pdf` files
   - Extracts text, tables, geometry
   - Saves JSON files to `output/`

---

## 📊 Data Flow Diagram

```
┌─────────────┐
│ Original    │
│ PDFs        │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Crop PDFs   │  adjust_crop.py
│ (5,90,595,  │  → *_cropped.pdf
│  262)       │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Extract     │  extract_text.py
│ Text        │  pdfplumber
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Normalize   │  text_normalization.py
│ - Whitespace│  - Persian digits
│ - BIDI      │  - Clean text
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Extract     │  extract_text.py
│ Tables      │  → DataFrame
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Export JSON │  save_results()
│ output/*.   │  → Clean JSON
│ json        │
└─────────────┘
```

---

## 🎯 Key Technologies

1. **PyMuPDF (fitz):** PDF manipulation (cropping)
2. **pdfplumber:** Text and table extraction
3. **python-bidi:** RTL text handling (BIDI algorithm)
4. **pandas:** Table data structure
5. **pydantic:** Configuration management

---

## 🔍 Important Concepts

### Visual Order vs Logical Order

**Visual Order (from PDF):**
- Text stored as it appears on screen
- For RTL: characters are backwards
- Example: `:ﺐﺼﻧ ﺦﯾﺭﺎﺗ` (garbled)

**Logical Order (after BIDI):**
- Text in proper reading order
- Characters in correct sequence
- Example: `تاریخ نصب:` (readable)

### Why BIDI is Critical

PDFs store RTL text in visual order because:
- PDF format prioritizes visual appearance
- Text rendering engine handles display
- But for text extraction, we need logical order

The BIDI algorithm:
- Analyzes text direction
- Reorders characters correctly
- Preserves mixed LTR/RTL content

---

## 📦 Output Structure

Each JSON file contains:

```json
{
  "source_file": "1_cropped.pdf",
  "text": "Full extracted text...",
  "table": {
    "headers": ["Column1", "Column2", ...],
    "rows": [
      ["value1", "value2", ...],
      ["value3", "value4", ...]
    ],
    "row_count": 76,
    "column_count": 34
  },
  "table_info": {
    "rows": 76,
    "columns": 34
  }
}
```

---

## 🛠️ Customization

### Adjust Crop Coordinates
Edit `adjust_crop.py`:
```python
x0 = 5   # Left edge
y0 = 90  # Top edge
x1 = 595 # Right edge
y1 = 262 # Bottom edge
```

### Change Output Format
Edit `extract_text.py`:
```python
extractor.config.output_formats = ["json", "csv", "txt"]
```

### Disable Normalization
Edit `config.py`:
```python
NormalizationConfig(
    normalize_persian_numbers=False,
    handle_bidi=False
)
```

---

## ✅ Summary

The pipeline:
1. **Crops** PDFs to table region
2. **Extracts** text and tables using pdfplumber
3. **Normalizes** text (whitespace, digits, BIDI)
4. **Structures** data into clean JSON format
5. **Handles** RTL text correctly via BIDI algorithm

**Result:** Clean, structured JSON files with properly ordered Persian text and table data ready for further processing.
