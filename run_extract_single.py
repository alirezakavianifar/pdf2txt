import sys
import re
from pathlib import Path

# Helper to normalize Persian/Arabic-Indic digits to Western digits
persian_digits = '۰۱۲۳۴۵۶۷۸۹'
arabic_indic_digits = '٠١٢٣٤٥٦٧٨٩'
trans_table = {ord(c): str(i) for i, c in enumerate(persian_digits)}
trans_table.update({ord(c): str(i) for i, c in enumerate(arabic_indic_digits)})

if len(sys.argv) < 2:
    print('Usage: run_extract_single.py <pdf_path>')
    sys.exit(1)

pdf_path = sys.argv[1]

# Import extractor
from extract_text import PDFTextExtractor

ext = PDFTextExtractor()
res = ext.extract_all(pdf_path, page_num=0)
text = res.get('text') or ''

# Normalize digits
norm_text = text.translate(trans_table)
# Replace Arabic comma '،' and Arabic thousands separators if any
norm_text = norm_text.replace('،', ',')

# Find number-like tokens (digits, commas, dots)
matches = re.findall(r"[\d,\.]+", norm_text)
# Filter out short tokens
numbers = [m.strip().strip('.,') for m in matches if len(re.sub(r'[,\.]','',m))>=1]

print('---EXTRACTED TEXT---')
print(text)
print('---NUMBERS FOUND---')
for n in numbers:
    print(n)

# Also write simple JSON summary
import json
summary = {'pdf': str(Path(pdf_path).name), 'numbers': numbers, 'text_excerpt': norm_text[:500]}
print('\n---JSON SUMMARY---')
print(json.dumps(summary, ensure_ascii=False, indent=2))
