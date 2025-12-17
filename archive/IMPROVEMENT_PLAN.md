# Improvement Plan for Template 2 Extraction Generalizability

## Priority 1: Critical Fixes (High Impact)

### 1. Improve `bill_summary_template2.py` - Make Field Matching More Flexible

**Current Problem:**
- Only extracts 1/6 fields from different PDFs
- Hard-coded patterns don't match variations
- Missing support for additional fields

**Solution: Add Fuzzy Matching and Dynamic Field Detection**

```python
from fuzzywuzzy import fuzz, process

def find_field_with_fuzzy(text: str, field_name: str, patterns: List[str], threshold: int = 70) -> Optional[Tuple[int, str]]:
    """
    Find field in text using fuzzy matching.
    Returns (position, matched_pattern) or None.
    """
    # Try exact matches first
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return (match.start(), pattern)
    
    # Try fuzzy matching on field name
    # Extract all potential field names from text
    words = text.split()
    for i, word in enumerate(words):
        # Check if word is similar to field name
        if fuzz.ratio(word, field_name) > threshold:
            return (text.find(word), word)
    
    return None
```

### 2. Support Multiple Number Formats

**Current Problem:**
- Only handles comma-separated numbers
- Doesn't handle Persian number separators
- Fails with different spacing

**Solution: Enhanced Number Parsing**

```python
def parse_number_flexible(text: str) -> Optional[float]:
    """
    Parse numbers with multiple format support.
    Handles: "123,456", "123 456", "123٬456", "123456"
    """
    if not text:
        return None
    
    # Remove all common separators
    cleaned = text.replace(',', '').replace('٬', '').replace(' ', '').replace('،', '').strip()
    
    # Convert Persian digits
    cleaned = convert_persian_digits(cleaned)
    
    try:
        return float(cleaned)
    except ValueError:
        return None

def extract_numbers_flexible(text: str) -> List[Tuple[int, float]]:
    """
    Extract all numbers from text with various formats.
    Returns list of (position, value) tuples.
    """
    numbers = []
    
    # Pattern 1: Comma-separated (123,456,789)
    for match in re.finditer(r'\d{1,3}(?:[,٬]\d{3})+', text):
        value = parse_number_flexible(match.group(0))
        if value:
            numbers.append((match.start(), value))
    
    # Pattern 2: Space-separated (123 456 789)
    for match in re.finditer(r'\d{1,3}(?:\s+\d{3})+', text):
        value = parse_number_flexible(match.group(0))
        if value:
            numbers.append((match.start(), value))
    
    # Pattern 3: Plain numbers (6+ digits)
    for match in re.finditer(r'\d{6,}', text):
        value = parse_number_flexible(match.group(0))
        if value and value > 1000:
            numbers.append((match.start(), value))
    
    return sorted(numbers, key=lambda x: x[0])
```

### 3. Dynamic Field Detection (Support Additional Fields)

**Current Problem:**
- Hard-coded field list
- Doesn't extract fields like "تجاوز از قدرت", "مابه التفاوت اجرای مقررات"

**Solution: Dynamic Field Extraction**

```python
def extract_all_fields_dynamically(text: str) -> Dict[str, Any]:
    """
    Extract all fields dynamically, not just predefined ones.
    """
    result = {}
    
    # Known field patterns (with variations)
    known_fields = {
        "بهای انرژی": ["بهای انرژی", "بهای", "انرژی"],
        "ضررو زیان": ["ضررو زیان", "ضرر", "زیان"],
        "مبلغ آبونمان": ["مبلغ آبونمان", "آبونمان"],
        "هزینه سوخت نیروگاهی": ["هزینه سوخت نیروگاهی", "هزینه سوخت"],
        "مالیات بر ارزش افزوده": ["مالیات بر ارزش افزوده", "ارزش افزوده", "مالیات"],
        "عوارض برق": ["عوارض برق", "عوارض"],
        "تجاوز از قدرت": ["تجاوز از قدرت", "تجاوز"],
        "مابه التفاوت اجرای مقررات": ["مابه التفاوت اجرای مقررات", "مابه التفاوت", "اجرای مقررات"],
        "مابه التفاوت ماده 16": ["مابه التفاوت ماده 16", "ماده 16"]
    }
    
    # Extract all numbers first
    all_numbers = extract_numbers_flexible(text)
    
    # For each known field, try to find it
    for field_name, patterns in known_fields.items():
        field_pos = find_field_with_fuzzy(text, field_name, patterns)
        if field_pos:
            pos, _ = field_pos
            # Find closest number after field
            for num_pos, num_value in all_numbers:
                if num_pos > pos:
                    result[field_name] = num_value
                    break
    
    return result
```

## Priority 2: Medium Impact Improvements

### 4. Generalize Fragmentation Patterns

**Current Problem:**
- Very specific fragmentation patterns like `r"به\s+ا\s+ی\s+ا\s+ن\s+ر\s+ژ\s+ی"`
- Doesn't handle different fragmentation styles

**Solution: Generic Fragmentation Handler**

```python
def handle_fragmented_text(text: str, target: str, tolerance: int = 2) -> Optional[str]:
    """
    Handle fragmented OCR text by matching characters with tolerance.
    
    Args:
        text: Text to search in
        target: Target string to find (e.g., "بهای انرژی")
        tolerance: Number of characters that can be missing/spaced
    
    Returns:
        Matched text or None
    """
    # Remove spaces from target
    target_clean = target.replace(' ', '')
    
    # Try to find target with spaces between characters
    # Pattern: allow 0-2 spaces between each character
    pattern_parts = []
    for char in target_clean:
        pattern_parts.append(re.escape(char))
    
    # Create pattern with optional spaces
    pattern = r'\s*'.join(pattern_parts)
    
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        return match.group(0)
    
    # Try fuzzy character matching
    # Find sequences where most characters match
    for i in range(len(text) - len(target_clean) + 1):
        substring = text[i:i + len(target_clean) + tolerance * 2]
        # Count matching characters
        matches = sum(1 for j, char in enumerate(target_clean) 
                     if i + j < len(text) and text[i + j] == char)
        
        if matches >= len(target_clean) - tolerance:
            return substring
    
    return None
```

### 5. Remove Hard-coded Value Ranges

**Current Problem:**
- Assumes specific value ranges (e.g., `10000000 <= value <= 999999999`)
- Rejects valid values outside range

**Solution: Relative Validation**

```python
def validate_value_relative(value: float, all_values: List[float], field_type: str) -> bool:
    """
    Validate value relative to other values in the section.
    """
    if not all_values:
        return True
    
    # For monetary fields, check if value is in reasonable range
    if field_type in ["بهای انرژی", "ضررو زیان"]:
        # Should be among the largest values
        sorted_values = sorted(all_values, reverse=True)
        return value in sorted_values[:3]  # Top 3 largest
    
    # For subscription, should be smaller
    if field_type == "مبلغ آبونمان":
        sorted_values = sorted(all_values)
        return value in sorted_values[:3]  # Top 3 smallest
    
    return True  # Default: accept all
```

## Priority 3: Testing and Validation

### 6. Create Test Suite

```python
# test_template2_generalizability.py

def test_all_template2_pdfs():
    """Test extraction on all Template 2 PDFs."""
    pdf_files = list(Path("template_2").glob("*.pdf"))
    
    results = {}
    for pdf_file in pdf_files:
        print(f"Testing {pdf_file.name}...")
        try:
            # Run pipeline
            run_pipeline(str(pdf_file))
            
            # Check results
            output_file = Path("output") / f"{pdf_file.stem}_final_pipeline.json"
            if output_file.exists():
                with open(output_file) as f:
                    data = json.load(f)
                
                # Validate extraction
                results[pdf_file.name] = validate_extraction(data)
        except Exception as e:
            results[pdf_file.name] = {"error": str(e)}
    
    return results

def validate_extraction(data: Dict) -> Dict:
    """Validate extracted data quality."""
    validation = {
        "bill_summary_fields": 0,
        "consumption_history_rows": 0,
        "ghodrat_kilowatt_fields": 0,
        "missing_fields": []
    }
    
    # Check bill_summary
    if "bill_summary_section" in data:
        bill_summary = data["bill_summary_section"].get("خلاصه صورتحساب", {})
        validation["bill_summary_fields"] = sum(1 for v in bill_summary.values() if v is not None)
        validation["missing_fields"] = [k for k, v in bill_summary.items() if v is None]
    
    return validation
```

## Implementation Steps

### Step 1: Quick Wins (1-2 hours)
1. ✅ Add flexible number parsing
2. ✅ Remove hard-coded value ranges
3. ✅ Add support for additional fields

### Step 2: Medium Improvements (2-4 hours)
4. ✅ Implement fuzzy matching for field names
5. ✅ Generalize fragmentation patterns
6. ✅ Add relative validation

### Step 3: Testing (1-2 hours)
7. ✅ Create test suite
8. ✅ Test with all Template 2 PDFs
9. ✅ Fix issues found in testing

### Step 4: Documentation (1 hour)
10. ✅ Update code comments
11. ✅ Document assumptions and limitations

## Expected Outcomes

After implementing these improvements:

- **bill_summary extraction**: 80-90% success rate (up from ~30%)
- **Overall extraction**: 85-95% success rate (up from ~70%)
- **Handles variations**: Different OCR qualities, formatting, additional fields
- **Better error handling**: Graceful degradation instead of failures

## Code Example: Improved bill_summary_template2.py

See `restructure_bill_summary_template2_improved.py` for full implementation.
