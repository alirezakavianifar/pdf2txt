# PDF to Text Extraction Pipeline

A clean, efficient pipeline for extracting structured text and table data from Persian/Arabic PDFs (energy consumption bills).

## 📁 Project Structure

```
pdf2txt/
├── adjust_crop.py          # Step 1: Crop PDFs to table region
├── extract_text.py         # Step 2: Extract text & tables → JSON
├── config.py               # Configuration management
├── text_normalization.py   # Text cleaning & BIDI handling
├── geometry_extraction.py  # Table structure extraction
├── requirements.txt        # Dependencies
└── template1/              # Input PDFs directory
    └── output/             # Output JSON files
```

## 🚀 Quick Start

### Step 1: Crop PDFs
```bash
python adjust_crop.py
```
- Crops all PDFs in `template1/` to table region
- Creates `*_cropped.pdf` files

### Step 2: Extract Text
```bash
python extract_text.py
```
- Processes all `*_cropped.pdf` files
- Extracts text, tables, and geometry
- Saves clean JSON files to `output/`

## 📦 Dependencies

Install from `requirements.txt`:
```bash
pip install -r requirements.txt
```

## ⚙️ Configuration

Edit `config.py` or modify settings in `extract_text.py`:
- Crop coordinates
- Extraction settings
- Normalization options
- Output formats

## 📊 Output Format

Each cropped PDF produces one JSON file:
```json
{
  "source_file": "1_cropped.pdf",
  "text": "Extracted and normalized text...",
  "table": {
    "headers": ["Column1", "Column2", ...],
    "rows": [["data1", "data2", ...], ...],
    "row_count": 76,
    "column_count": 34
  },
  "table_info": {
    "rows": 76,
    "columns": 34
  }
}
```

## 🔧 Key Features

- ✅ Handles Persian/Arabic RTL text correctly
- ✅ Converts Persian digits to ASCII
- ✅ Extracts structured table data
- ✅ Clean JSON output format
- ✅ Batch processing support

## 📝 Pipeline Flow

```
Original PDFs → Crop (adjust_crop.py) → Extract (extract_text.py) → JSON Output
```

See `PIPELINE_EXPLANATION.md` for detailed documentation.
