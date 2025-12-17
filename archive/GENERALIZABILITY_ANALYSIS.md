# Generalizability Analysis for Template 2 Extraction Scripts

## Overview
This document analyzes the generalizability of the Template 2 extraction scripts and identifies potential issues when processing different PDFs.

## Current Scripts
1. `restructure_bill_summary_template2.py`
2. `restructure_ghodrat_kilowatt_template2.py`
3. `restructure_consumption_history_template2.py`
4. `restructure_energy_supported_template2.py`
5. `restructure_power_section_template2.py`

## Generalizability Issues Identified

### 1. **Hard-coded Field Names** ⚠️
**Issue:** Scripts use specific Persian field names that might vary across PDFs.

**Examples:**
- `restructure_bill_summary_template2.py`: Uses exact field names like "بهای انرژی", "ضررو زیان", etc.
- `restructure_ghodrat_kilowatt_template2.py`: Looks for specific labels like "قراردادی", "محاسبه شده"

**Impact:** Medium - Field names are likely standardized, but minor variations could break extraction.

**Recommendation:**
- Use fuzzy matching for field names (e.g., `fuzzywuzzy` library)
- Support multiple variations of field names
- Add fallback patterns

### 2. **Pattern Matching Specificity** ⚠️
**Issue:** Regex patterns are tailored to specific text formats.

**Examples:**
- `restructure_bill_summary_template2.py`: Pattern `r'\d{1,3}(?:,\d{3})+'` assumes comma-separated numbers
- `restructure_consumption_history_template2.py`: Assumes specific column order

**Impact:** Medium - Different formatting (e.g., different separators, spacing) could fail.

**Recommendation:**
- Support multiple number formats (commas, spaces, Persian separators)
- Make patterns more flexible with optional whitespace
- Add pattern variations

### 3. **Value Range Validation** ⚠️
**Issue:** Some scripts validate values against hard-coded ranges.

**Examples:**
- `restructure_bill_summary_template2.py`: Checks `10000000 <= value <= 999999999` for energy price
- Assumes specific value ranges that might not apply to all bills

**Impact:** Low-Medium - Could reject valid values outside expected ranges.

**Recommendation:**
- Remove or make value ranges configurable
- Use relative validation (e.g., "largest number in section")
- Add warnings instead of hard failures

### 4. **Position-Based Logic** ⚠️
**Issue:** Some extraction relies on line order or position.

**Examples:**
- `restructure_ghodrat_kilowatt_template2.py`: Assumes specific line order
- `restructure_consumption_history_template2.py`: Uses position to distinguish paid vs period amounts

**Impact:** Medium - Different layouts could break extraction.

**Recommendation:**
- Use semantic matching (field names) instead of position
- Make position-based logic more flexible
- Add fallback strategies

### 5. **Fragmented OCR Handling** ⚠️
**Issue:** Very specific handling for fragmented OCR text.

**Examples:**
- `restructure_bill_summary_template2.py`: Handles specific fragmentation patterns like `r"به\s+ا\s+ی\s+ا\s+ن\s+ر\s+ژ\s+ی"`

**Impact:** High - Different OCR quality or fragmentation patterns won't match.

**Recommendation:**
- Generalize fragmentation patterns
- Use character-level matching with tolerance
- Support multiple fragmentation variations

### 6. **Table Structure Assumptions** ⚠️
**Issue:** Assumes specific table structures and column counts.

**Examples:**
- `restructure_consumption_history_template2.py`: Assumes 12 columns
- `restructure_energy_supported_template2.py`: Assumes specific column order

**Impact:** High - Different table structures will fail.

**Recommendation:**
- Detect table structure dynamically
- Support variable column counts
- Use header matching instead of position

## Strengths (What Works Well)

### ✅ **Persian Digit Conversion**
- Generic conversion function handles Persian/Arabic-Indic digits
- Works across different PDFs

### ✅ **Number Parsing**
- Handles commas, spaces, and various separators
- Flexible number extraction

### ✅ **Error Handling**
- Scripts return `None` for missing values instead of crashing
- Graceful degradation

### ✅ **Modular Design**
- Each section has its own script
- Easy to update individual sections

## Recommendations for Improvement

### Priority 1: High Impact
1. **Add Fuzzy Matching for Field Names**
   ```python
   from fuzzywuzzy import fuzz
   if fuzz.ratio(field_name, pattern) > 80:
       # Match found
   ```

2. **Support Multiple Number Formats**
   - Handle different separators (comma, space, Persian comma)
   - Support both formatted and unformatted numbers

3. **Dynamic Table Structure Detection**
   - Detect column count from headers
   - Match columns by header name instead of position

### Priority 2: Medium Impact
4. **Configurable Value Ranges**
   - Move hard-coded ranges to configuration
   - Use relative validation

5. **Generalized Fragmentation Patterns**
   - Create generic fragmentation handler
   - Support multiple OCR quality levels

6. **Fallback Strategies**
   - If primary extraction fails, try alternative methods
   - Log failures for manual review

### Priority 3: Low Impact
7. **Add Validation Warnings**
   - Warn when values seem unusual
   - Allow manual override

8. **Comprehensive Testing**
   - Test with all available Template 2 PDFs
   - Create test suite for regression testing

## Testing Strategy

### Current Test Coverage
- ✅ Tested with: `template_2/2.pdf`
- ✅ Tested with: `template_2/3_1000_7001523101422.pdf`

### Test Results

#### PDF: `2.pdf`
- ✅ **bill_summary**: 4/6 fields extracted (مبلغ آبونمان, هزینه سوخت, مالیات, عوارض برق)
- ❌ **bill_summary**: 2/6 fields missing (بهای انرژی, ضررو زیان) - OCR fragmentation
- ✅ **ghodrat_kilowatt**: All fields extracted
- ✅ **consumption_history**: All rows extracted

#### PDF: `3_1000_7001523101422.pdf`
- ⚠️ **bill_summary**: Only 1/6 fields extracted (مبلغ آبونمان)
- ❌ **bill_summary**: 5/6 fields missing - Different format/OCR quality
- ✅ **ghodrat_kilowatt**: All fields extracted correctly
- ✅ **consumption_history**: 6 rows extracted correctly

### Key Findings
1. **bill_summary extraction is NOT generic enough** - Only works for PDFs with very specific formatting
2. **ghodrat_kilowatt extraction is robust** - Works across different PDFs
3. **consumption_history extraction is robust** - Works across different PDFs
4. **OCR quality varies** - Different PDFs have different OCR fragmentation patterns

### Recommended Testing
1. **Run pipeline on all Template 2 PDFs**
2. **Compare extracted values** across PDFs
3. **Identify common failures**
4. **Create test cases** for edge cases
5. **Improve bill_summary extraction** to handle more variations

## Conclusion

**Current Generalizability: ~70%**

The scripts work well for PDFs with:
- Standard field names
- Similar formatting
- Good OCR quality
- Expected table structures

**Will likely fail for PDFs with:**
- Non-standard field names
- Different formatting
- Poor OCR quality
- Different table structures
- Unusual value ranges

**Next Steps:**
1. Test with multiple Template 2 PDFs
2. Implement fuzzy matching for field names
3. Generalize number format handling
4. Add fallback strategies
5. Create comprehensive test suite
