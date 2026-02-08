"""Restructure energy consumption table section for Template 6."""
import json
import re
from pathlib import Path


def convert_persian_digits(text):
    """Convert Persian/Arabic-Indic digits to regular digits."""
    persian_digits = '۰۱۲۳۴۵۶۷۸۹'
    arabic_indic_digits = '٠١٢٣٤٥٦٧٨٩'
    regular_digits = '0123456789'
    
    result = text
    for i, persian in enumerate(persian_digits):
        result = result.replace(persian, regular_digits[i])
    for i, arabic in enumerate(arabic_indic_digits):
        result = result.replace(arabic, regular_digits[i])
    
    return result


def parse_number(text: str):
    """
    Parse a number from a token.

    Handles:
    - Persian/Arabic-Indic digits
    - Thousands separators (`,` / `٬` / `،`)
    - Decimal separator as `.` or `/` or `,` (decimal-comma cases like `7,2`)
    """
    if not text or text == "." or text.strip() == "":
        return None

    t = convert_persian_digits(text)
    t = t.replace("٬", ",").replace("،", ",").replace(" ", "").strip()
    if not t or t == ".":
        return None

    # Normalize slash-decimal.
    if "/" in t and "." not in t:
        t = t.replace("/", ".")

    # Handle decimal-comma (e.g. 7,2 or 1,06) vs thousands-comma (e.g. 33,697,904).
    if "," in t and "." not in t:
        # thousands pattern
        if re.fullmatch(r"-?\d{1,3}(?:,\d{3})+", t):
            t = t.replace(",", "")
        # decimal comma pattern
        elif re.fullmatch(r"-?\d+,\d{1,2}", t):
            t = t.replace(",", ".")
        else:
            # ambiguous: prefer treating commas as thousands separators
            t = t.replace(",", "")

    try:
        if "." in t:
            return float(t)
        return int(t)
    except ValueError:
        return None


def normalize_reversed_thousands(text: str) -> str:
    """
    Fix common bidi/noise pattern where thousands separators appear "reversed"
    across RTL tokens, e.g. '200 روما,1' -> '1,200'.
    
    We swap the two numeric groups around a comma when there are non-digit
    characters between them.
    """
    if not text:
        return ""
    
    t = convert_persian_digits(text)
    
    # Replace the common noise token explicitly seen in Template 6 outputs.
    # ('روما' is a frequent bidi artifact of 'امور')
    t = t.replace("روما", " ")
    
    pattern = re.compile(r'(\d{1,3})\s*[^0-9,]{1,10},\s*(\d{1,3})')
    # Apply repeatedly in case there are multiple occurrences in the same line.
    prev = None
    while prev != t:
        prev = t
        t = pattern.sub(r'\2,\1', t)
    return t


def normalize_numeric_blob(text: str) -> str:
    """
    Normalize a potentially noisy numeric blob extracted from Template 6 PDFs.

    Key cases we handle:
    - "200 روما,1" -> "1,200"
    - "20 روما5,385,3" -> "5,385,320"  (prefix digits belong to the last thousands group)
    - Remove bidi noise tokens ("روما", "امور") while preserving digits and separators.
    """
    if not text:
        return ""

    t = convert_persian_digits(text)
    # Common bidi noise tokens in template 6 extraction
    t = t.replace("روما", " ").replace("امور", " ")
    t = normalize_reversed_thousands(t)

    # Fix split thousands where a 1-2 digit prefix actually belongs to the last group.
    # Examples:
    #   "20 5,385,3"  -> "5,385,320"
    #   "25 11,571,1" -> "11,571,125"
    split_thousands = re.compile(r"(\d{1,2})\s+(\d{1,3}(?:,\d{3})+),(\d{1,2})")
    prev = None
    while prev != t:
        prev = t
        t = split_thousands.sub(lambda m: f"{m.group(2)},{m.group(3)}{m.group(1)}", t)

    # Keep only digits/separators/minus and whitespace for easier tokenization.
    t = re.sub(r"[^0-9,./\\-]+", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t


def numbers_from_cell(cell_text: str) -> list:
    """Extract parsed numeric values from a single cell."""
    t = normalize_numeric_blob(str(cell_text or ""))
    if not t:
        return []
    tokens = re.findall(r"-?\d+(?:,\d+)*(?:[./]\d+)?", t)
    vals = []
    for tok in tokens:
        v = parse_number(tok)
        if v is None:
            continue
        vals.append(v)
    return vals


def pick_best_numeric(vals: list, *, prefer_int: bool = False):
    """Pick a representative numeric value from a list of parsed values."""
    if not vals:
        return None
    if prefer_int:
        int_like = [v for v in vals if isinstance(v, int) or (isinstance(v, float) and v.is_integer())]
        if int_like:
            return int(max(int_like, key=lambda x: abs(float(x))))
    return max(vals, key=lambda x: abs(float(x)))


def compute_read_energy(prev_val, cur_val, coeff_val, digits_val=None):
    """Compute read energy from counters and coefficient with a rollover-aware fallback."""
    if prev_val is None or cur_val is None or coeff_val in (None, 0):
        return None
    try:
        prev_f = float(prev_val)
        cur_f = float(cur_val)
        coeff_f = float(coeff_val)
    except (TypeError, ValueError):
        return None

    diff = cur_f - prev_f
    # Rollover correction only when values look like integers.
    if diff < 0 and digits_val is not None:
        try:
            d = int(digits_val)
            if d > 0 and float(prev_val).is_integer() and float(cur_val).is_integer():
                diff = (10 ** d) - prev_f + cur_f
        except Exception:
            pass

    energy = abs(diff) * coeff_f
    # snap near-integers to int
    if abs(energy - round(energy)) < 0.05:
        return int(round(energy))
    return float(round(energy, 3))


def extract_from_table_rows(table_rows: list) -> list[dict]:
    """
    Extract template-6 energy rows from `table.rows` when row labels are not
    reliably extracted.

    Template 6 bills often have garbled headers/labels, but numeric columns are
    stable. We infer key columns from the 'digits' column location and then map
    nearby columns by relative position.
    """
    if not table_rows:
        return []

    # Skip the header-like first row if it contains mostly non-numeric text.
    candidate_rows = table_rows[:]
    if candidate_rows:
        header_nums = []
        for c in candidate_rows[0]:
            header_nums.extend(numbers_from_cell(c))
        if len(header_nums) <= 4:
            candidate_rows = candidate_rows[1:]

    # Remove completely empty / all-zero rows.
    cleaned_rows = []
    for r in candidate_rows:
        row_vals = []
        for c in r:
            row_vals.extend(numbers_from_cell(c))
        if not row_vals:
            continue
        if all((v == 0) for v in row_vals if isinstance(v, (int, float))):
            # keep only if there is a strong signal (some bills put a non-zero cost elsewhere)
            continue
        cleaned_rows.append(r)

    if not cleaned_rows:
        return []

    max_cols = max(len(r) for r in cleaned_rows)
    # Build per-column representative values to detect key columns.
    col_samples: list[list] = [[] for _ in range(max_cols)]
    for r in cleaned_rows:
        for ci in range(max_cols):
            cell = r[ci] if ci < len(r) else ""
            vals = numbers_from_cell(cell)
            rep = pick_best_numeric(vals)
            if rep is not None:
                col_samples[ci].append(rep)

    # Digits column: mostly small ints (4..10)
    def digits_score(ci: int) -> int:
        score = 0
        for v in col_samples[ci]:
            if isinstance(v, int) and 3 <= v <= 10:
                score += 1
        return score

    digits_col = max(range(max_cols), key=digits_score)
    # Coefficient is typically immediately to the left in Template 6 layout.
    coeff_col = digits_col - 1 if digits_col - 1 >= 0 else None

    # Fallback coefficient column if adjacency doesn't look right.
    def coeff_score(ci: int) -> int:
        score = 0
        for v in col_samples[ci]:
            if isinstance(v, int) and 1 <= v <= 100000:
                score += 1
        return score

    if coeff_col is None or coeff_score(coeff_col) == 0:
        coeff_col = max(range(max_cols), key=coeff_score)

    # In Template 6 numeric tables, current/previous are to the right of digits.
    current_col = digits_col + 1 if digits_col + 1 < max_cols else None
    prev_col = digits_col + 2 if digits_col + 2 < max_cols else None

    # Cost column: largest magnitude integer column.
    def cost_score(ci: int) -> float:
        ints = [int(v) for v in col_samples[ci] if isinstance(v, int) and v >= 1000]
        if not ints:
            return 0.0
        return float(sum(ints)) / max(1, len(ints))

    cost_col = max(range(max_cols), key=cost_score)

    # Relative mapping around coeff column (common stable layout).
    read_energy_col = coeff_col - 1 if coeff_col is not None and coeff_col - 1 >= 0 else None
    bilateral_col = coeff_col - 2 if coeff_col is not None and coeff_col - 2 >= 0 else None
    excess_col = coeff_col - 3 if coeff_col is not None and coeff_col - 3 >= 0 else None
    green_col = coeff_col - 4 if coeff_col is not None and coeff_col - 4 >= 0 else None
    leap_col = coeff_col - 5 if coeff_col is not None and coeff_col - 5 >= 0 else None
    supplied_col = coeff_col - 6 if coeff_col is not None and coeff_col - 6 >= 0 else None

    # Tariff columns are typically the first two columns in the extracted table.
    tariff_a_col = 0 if max_cols > 0 else None
    tariff_d_col = 1 if max_cols > 1 else None

    ordered_descriptions = ["میان بار", "اوج بار", "کم بار", "راکتیو", "جمعه"]
    out_rows: list[dict] = []

    for ridx, r in enumerate(cleaned_rows):
        if ridx >= len(ordered_descriptions):
            break

        def cell(ci: int):
            if ci is None:
                return ""
            return r[ci] if ci < len(r) else ""

        digits_val = pick_best_numeric(numbers_from_cell(cell(digits_col)), prefer_int=True)
        coeff_val = pick_best_numeric(numbers_from_cell(cell(coeff_col)), prefer_int=True)
        prev_val = pick_best_numeric(numbers_from_cell(cell(prev_col)))
        cur_val = pick_best_numeric(numbers_from_cell(cell(current_col)))

        # Costs are large ints; pick the largest int-like in the cost cell first, else in entire row.
        cost_vals = numbers_from_cell(cell(cost_col))
        cost_val = pick_best_numeric(cost_vals, prefer_int=True)
        if cost_val is None:
            # fallback: largest integer in row
            all_ints = []
            for ci in range(len(r)):
                all_ints.extend([int(v) for v in numbers_from_cell(r[ci]) if isinstance(v, int)])
            cost_val = max(all_ints, default=None)

        read_val = pick_best_numeric(numbers_from_cell(cell(read_energy_col)), prefer_int=True)
        bilateral_val = pick_best_numeric(numbers_from_cell(cell(bilateral_col)), prefer_int=True)
        excess_val = pick_best_numeric(numbers_from_cell(cell(excess_col)), prefer_int=True)
        green_val = pick_best_numeric(numbers_from_cell(cell(green_col)), prefer_int=True)
        leap_val = pick_best_numeric(numbers_from_cell(cell(leap_col)), prefer_int=True)
        supplied_val = pick_best_numeric(numbers_from_cell(cell(supplied_col)), prefer_int=True)

        computed_read = compute_read_energy(prev_val, cur_val, coeff_val, digits_val=digits_val)

        # Prefer computed read energy when available and parsed read looks implausible.
        if computed_read is not None:
            if read_val is None:
                read_val = computed_read
            else:
                try:
                    if float(read_val) <= 0 or abs(float(read_val) - float(computed_read)) > max(50.0, 0.25 * float(computed_read)):
                        read_val = computed_read
                except Exception:
                    read_val = computed_read

        # Default zeros for energy purchase columns when missing.
        bilateral_val = 0 if bilateral_val is None else bilateral_val
        excess_val = 0 if excess_val is None else excess_val
        green_val = 0 if green_val is None else green_val
        leap_val = 0 if leap_val is None else leap_val

        # If supplied is missing/implausible, use read energy minus other supplies.
        if supplied_val is None and read_val is not None:
            try:
                supplied_val = max(0, int(round(float(read_val) - float(bilateral_val) - float(excess_val) - float(green_val) - float(leap_val))))
            except Exception:
                supplied_val = read_val

        tariff_a_val = pick_best_numeric(numbers_from_cell(cell(tariff_a_col)), prefer_int=True) if tariff_a_col is not None else None
        tariff_d_val = pick_best_numeric(numbers_from_cell(cell(tariff_d_col)), prefer_int=True) if tariff_d_col is not None else None

        row_data = {
            "شرح مصارف": ordered_descriptions[ridx],
            "شمارنده قبلی": prev_val,
            "شمارنده فعلی": cur_val,
            "تعداد ارقام": digits_val,
            "ضریب کنتور": coeff_val,
            "انرژی قرائت شده": read_val,
            "انرژی خریداری شده دوجانبه و بورس": bilateral_val,
            "انرژی مازاد خرید از بازار": excess_val,
            "انرژی خریداری شده دو جانبه سبز": green_val,
            "مصرف قانون جهش تولید": leap_val,
            "انرژی تامین شده توسط توزیع": supplied_val,
            "بهای انرژی تامین شده توسط توزیع": cost_val,
            "انرژی مشمول تعرفه (۴- الف)": tariff_a_val,
            "انرژی مشمول تعرفه (۴-د)": tariff_d_val,
        }
        out_rows.append(row_data)

    return out_rows


def extract_energy_consumption_data(text, table_data=None):
    """Extract energy consumption table data from text.
    
    Expected columns (14 columns):
    - شرح مصارف (Description): میان بار, اوج بار, کم بار, جمعه, راکتیو
    - شمارنده قبلی (Previous Counter)
    - شمارنده فعلی (Current Counter)
    - تعداد ارقام (Number of Digits): 6
    - ضریب کنتور (Meter Coefficient): 4,000
    - انرژی قرائت شده (Read Energy)
    - انرژی خریداری شده دوجانبه و بورس (Energy Purchased Bilaterally and from Exchange)
    - انرژی مازاد خرید از بازار (Excess Energy Purchased from Market)
    - انرژی خریداری شده دو جانبه سبز (Green Bilaterally Purchased Energy)
    - مصرف قانون جهش تولید (Consumption under Production Leap Law)
    - انرژی تامین شده توسط توزیع (Energy Supplied by Distribution)
    - بهای انرژی تامین شده توسط توزیع (Cost of Energy Supplied by Distribution)
    - انرژی مشمول تعرفه (۴- الف) (Energy Subject to Tariff 4-A)
    - انرژی مشمول تعرفه (۴-د) (Energy Subject to Tariff 4-D)
    """
    normalized_text = convert_persian_digits(text)
    
    # Initialize result structure
    result = {
        "جدول مصارف انرژی": {
            "rows": []
        }
    }
    
    # Try to use table data if available
    if table_data and 'rows' in table_data:
        # First attempt: if row labels are readable, map by label presence.
        labeled = []
        for row in table_data['rows']:
            if not row:
                continue
            row_text = " ".join(str(c or "") for c in row)
            if any(k in row_text for k in ["میان بار", "اوج بار", "کم بار", "جمعه", "راکتیو"]):
                labeled.append(row)

        if labeled:
            # Best-effort label-based mapping: try to locate the row label anywhere in the row.
            for row in labeled:
                row_text = " ".join(str(c or "") for c in row)
                desc = next((k for k in ["میان بار", "اوج بار", "کم بار", "راکتیو", "جمعه"] if k in row_text), "")
                nums = []
                for c in row:
                    nums.extend(numbers_from_cell(c))
                # Keep last 13 numeric columns in expected order (when present).
                if len(nums) > 13:
                    nums = nums[-13:]
                values = nums + [None] * (13 - len(nums))
                row_data = {
                    "شرح مصارف": desc,
                    "شمارنده قبلی": values[0],
                    "شمارنده فعلی": values[1],
                    "تعداد ارقام": values[2],
                    "ضریب کنتور": values[3],
                    "انرژی قرائت شده": values[4],
                    "انرژی خریداری شده دوجانبه و بورس": values[5] or 0,
                    "انرژی مازاد خرید از بازار": values[6] or 0,
                    "انرژی خریداری شده دو جانبه سبز": values[7] or 0,
                    "مصرف قانون جهش تولید": values[8] or 0,
                    "انرژی تامین شده توسط توزیع": values[9],
                    "بهای انرژی تامین شده توسط توزیع": values[10],
                    "انرژی مشمول تعرفه (۴- الف)": values[11],
                    "انرژی مشمول تعرفه (۴-د)": values[12],
                }
                result["جدول مصارف انرژی"]["rows"].append(row_data)
            if result["جدول مصارف انرژی"]["rows"]:
                return result

        # Generic Template 6 mapping when labels are not readable: infer columns from numeric layout.
        inferred_rows = extract_from_table_rows(table_data.get("rows") or [])
        if inferred_rows:
            result["جدول مصارف انرژی"]["rows"] = inferred_rows
            return result
    
    # Fallback: parse from text
    # Normalize common bidi/noise artifacts before line parsing.
    normalized_text = normalize_numeric_blob(normalized_text)
    lines = [line.strip() for line in normalized_text.split('\n') if line.strip()]
    
    # First try the more explicit description-based extraction in case
    # the row labels (e.g. "میان بار") are present in the text. This
    # keeps the logic compatible with any future Template 6 variants
    # where the extractor captures the row descriptions correctly.
    row_descriptions = [
        "میان بار",
        "اوج بار",
        "کم بار",
        "جمعه",
        "راکتیو"
    ]
    
    for desc in row_descriptions:
        for line in lines:
            if desc in line:
                numbers = re.findall(r'\d+(?:,\d+)*(?:[/\.]\d+)?', line)
                if numbers:
                    row_data = {
                        "شرح مصارف": desc,
                        "values": [parse_number(num) for num in numbers]
                    }
                    result["جدول مصارف انرژی"]["rows"].append(row_data)
                break
    
    # If we still have no rows, fall back to a numeric-pattern based
    # extraction that does not depend on the row descriptions being
    # readable. In many Template 6 PDFs, the row labels are rendered
    # as glyphs that the extractor can't decode, but the numeric values
    # in each row are reliable.
    if not result["جدول مصارف انرژی"]["rows"]:
        # Generic fallback: find "data-like" lines by number density.
        # Template 6 energy rows contain many numeric columns; even when the
        # coefficient value varies (1,200 / 4,000 / ...), the row still has
        # a high count of numeric tokens.
        candidate_lines = []
        for line in lines:
            numbers = re.findall(r'\d+(?:,\d+)*(?:[/\.]\d+)?', line)
            # Require enough numbers to likely be a table row (not headers).
            if len(numbers) >= 10:
                candidate_lines.append(numbers)
        
        # Expected row order for Template 6 energy consumption table.
        # Even when the labels are unreadable, the visual order of rows
        # in the template is stable, so we can assign them deterministically.
        ordered_descriptions = [
            "میان بار",
            "اوج بار",
            "کم بار",
            "جمعه",
            "راکتیو"
        ]
        
        # Mapping of numeric columns to semantic field names
        value_fields = [
            "شمارنده قبلی",
            "شمارنده فعلی",
            "تعداد ارقام",
            "ضریب کنتور",
            "انرژی قرائت شده",
            "انرژی خریداری شده دوجانبه و بورس",
            "انرژی مازاد خرید از بازار",
            "انرژی خریداری شده دو جانبه سبز",
            "مصرف قانون جهش تولید",
            "انرژی تامین شده توسط توزیع",
            "بهای انرژی تامین شده توسط توزیع",
            "انرژی مشمول تعرفه (۴- الف)",
            "انرژی مشمول تعرفه (۴-د)",
        ]
        
        for idx, numbers in enumerate(candidate_lines):
            # Ensure we only process up to the known number of template rows
            if idx >= len(ordered_descriptions):
                break
            
            # The table rows have a stable set of numeric columns; when we see
            # more than 13 numbers, keep the last 13 which usually correspond
            # to the actual row cells.
            if len(numbers) > 13:
                numbers = numbers[-13:]
            
            values = [parse_number(num) for num in numbers]
            row_data = {
                "شرح مصارف": ordered_descriptions[idx]
            }
            
            # Assign numbers to their respective fields in order
            for field_index, field_name in enumerate(value_fields):
                if field_index < len(values):
                    row_data[field_name] = values[field_index]
                else:
                    row_data[field_name] = None
            
            result["جدول مصارف انرژی"]["rows"].append(row_data)
    
    return result


def restructure_energy_consumption_template6_json(json_path: Path, output_path: Path):
    """Restructure extracted JSON to include energy consumption table data for Template 6."""
    print(f"Restructuring Energy Consumption Table (Template 6) from {json_path}...")
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        text = data.get('text', '')
        table_data = data.get('table', {})
        
        # Extract energy consumption data
        energy_data = extract_energy_consumption_data(text, table_data)
        
        # Build restructured data
        result = energy_data
        
        # Save restructured JSON
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"  - Saved to {output_path}")
        row_count = len(energy_data["جدول مصارف انرژی"]["rows"])
        print(f"  - Extracted {row_count} consumption rows")
        
        return result
        
    except Exception as e:
        print(f"Error restructuring Energy Consumption T6: {e}")
        import traceback
        traceback.print_exc()
        return None

