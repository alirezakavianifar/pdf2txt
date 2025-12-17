# Folder Structure & File Organization

## 📁 Current Structure

```
template1/
├── 1.pdf                                    # Original PDF (NOT processed)
├── 1/                                       # Folder for PDF "1"
│   └── energy_supported_section.pdf        # Cropped section (PROCESSED)
├── 4_510_9019722204129.pdf                 # Original PDF (NOT processed)
├── 4_510_9019722204129/                    # Folder for this PDF
│   └── energy_supported_section.pdf        # Cropped section (PROCESSED)
└── ... (same pattern for all PDFs)

output/
├── 1_energy_supported_section.json         # Extracted data
├── 4_510_9019722204129_energy_supported_section.json
└── ... (one JSON per section)
```

## 🔄 What Gets Processed

### During Cropping (`adjust_crop.py`):
- **Input:** `template1/{pdf_name}.pdf` (original PDFs)
- **Output:** `template1/{pdf_name}/{section_name}.pdf` (cropped sections)

### During Extraction (`extract_text.py`):
- **Input:** `template1/{pdf_name}/{section_name}.pdf` (cropped section PDFs)
- **Output:** `output/{pdf_name}_{section_name}.json` (extracted data)

## ✅ Answer: Cropped PDFs Are Read

**The extraction script reads the CROPPED section PDFs**, not the original PDFs.

- ✅ Reads: `template1/1/energy_supported_section.pdf`
- ❌ Does NOT read: `template1/1.pdf`

This ensures:
1. Only relevant sections are extracted
2. Each section can be processed independently
3. Multiple sections from same PDF can be extracted separately
4. Output files have meaningful names: `{pdf_name}_{section_name}.json`

## 📝 Adding More Sections

To crop additional sections, edit `adjust_crop.py` and add to `crop_sections` list:

```python
crop_sections = [
    {
        "name": "energy_supported_section",
        "description": "Supported Energy Values Section",
        "x0": 5, "y0": 90, "x1": 595, "y1": 262
    },
    {
        "name": "regulation_difference_section",  # New section
        "description": "Regulation Implementation Difference",
        "x0": 5, "y0": 263, "x1": 595, "y1": 400  # Different coordinates
    },
]
```

Each section will be saved as:
- `template1/{pdf_name}/energy_supported_section.pdf`
- `template1/{pdf_name}/regulation_difference_section.pdf`

And extracted to:
- `output/{pdf_name}_energy_supported_section.json`
- `output/{pdf_name}_regulation_difference_section.json`
