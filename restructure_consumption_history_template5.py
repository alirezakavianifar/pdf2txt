"""Restructure consumption history section for Template 5."""
import json
import re
from pathlib import Path

# #region agent log
LOG_PATH = r"e:\projects\pdf2txt\.cursor\debug.log"
def debug_log(location, message, data, hypothesis_id=None):
    try:
        with open(LOG_PATH, 'a', encoding='utf-8') as f:
            import time
            log_entry = {
                "timestamp": int(time.time() * 1000),
                "location": location,
                "message": message,
                "data": data,
                "sessionId": "debug-session",
                "runId": "run1",
                "hypothesisId": hypothesis_id
            }
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
    except: pass
# #endregion


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


def parse_number(text):
    """Parse a number, removing commas and handling Persian digits."""
    if not text:
        return None
    
    text = convert_persian_digits(text)
    # Remove commas used as thousand separators
    text = text.replace(',', '').replace(' ', '')
    
    try:
        return int(text)
    except ValueError:
        try:
            return float(text)
        except ValueError:
            return None


def extract_consumption_history_data(text, table_data=None):
    """Extract consumption history table data from text.
    
    Header: سوابق مصارف مبالغ و پرداختهای ادوار گذشته
    Columns: دوره/سال, تاریخ قرائت, مصارف کیلووات ساعت (میان باری, اوج بار, کم باری, اوج بار جمعه, راکتیو), 
             مبلغ دوره ریال, مهلت پرداخت, مبلغ پرداختی, تاریخ پرداخت
    Multiple rows for different periods
    """
    normalized_text = convert_persian_digits(text)
    
    result = {
        "سوابق مصارف مبالغ و پرداختهای ادوار گذشته": {
            "rows": []
        }
    }
    
    # Skip table_data path - table extraction is unreliable for consumption history section
    # Always use text parsing which works correctly
    
    # Fallback: parse from text
    # Format: "MM YYYY YYYY/MM/DD <consumption values> YYYY/MM/DD <payment values> <amount>"
    # Example: "08 1404 1404/08/01 156 0 5 1404/08/17 0 342 291 10955000"
    lines = [line.strip() for line in normalized_text.split('\n') if line.strip()]
    
    date_pattern = r'\d{4}/\d{2}/\d{2}'
    # Period format is MM YYYY (month year), not YYYY MM
    period_pattern = r'\d{2}\s+\d{4}'  # Period format like "08 1404"
    
    for line in lines:
        # Check if line contains period pattern (MM YYYY)
        if re.search(period_pattern, line):
            # #region agent log
            debug_log("restructure_consumption_history_template5.py:69", "Processing line", {"line": line}, "A")
            # #endregion
            
            # Extract period (MM YYYY)
            period_match = re.search(r'(\d{2})\s+(\d{4})', line)
            if not period_match:
                continue  # Skip if we can't extract period
            
            period = f"{period_match.group(2)} {period_match.group(1)}"  # Format as YYYY MM
            
            # Extract reading date (first date in the line)
            # Payment deadline and payment date are now cropped out
            dates = re.findall(date_pattern, line)
            reading_date = dates[0] if len(dates) > 0 else None
            # Payment fields are cropped out - set to None
            payment_deadline = None
            payment_date = None
            
            # Skip if we don't have at least period and reading date
            if not reading_date:
                continue
            
            # Parse the row structure:
            # Format: "MM YYYY YYYY/MM/DD <اوج بار> <اوج بار جمعه> <راکتیو> <میان باری> <کم باری> <مبلغ دوره ریال>"
            # Example: "08 1404 1404/08/01 156 0 5 342 291 10955000"
            # After period (MM YYYY) and reading date: اوج بار, اوج بار جمعه, راکتیو, میان باری, کم باری, مبلغ دوره ریال
            # Note: The three leftmost columns (تاریخ پرداخت, مبلغ پرداختی, مهلت پرداخت) are now cropped out
            
            # Split the line into parts to extract values more precisely
            # Format: "MM YYYY YYYY/MM/DD <اوج بار> <اوج بار جمعه> <راکتیو> <میان باری> <کم باری> <مبلغ دوره ریال>"
            parts = line.split()
            
            # #region agent log
            debug_log("restructure_consumption_history_template5.py:98", "Line split into parts", {"parts": parts, "parts_count": len(parts)}, "B")
            # #endregion
            
            # Find the index of the reading date (format YYYY/MM/DD)
            date_idx = -1
            for i, part in enumerate(parts):
                if re.match(r'\d{4}/\d{2}/\d{2}', part):
                    date_idx = i
                    break
            
            # #region agent log
            debug_log("restructure_consumption_history_template5.py:107", "Date index found", {"date_idx": date_idx, "reading_date": reading_date}, "B")
            # #endregion
            
            if date_idx == -1:
                continue  # Skip if we can't find the date
            
            # Extract numbers after the date
            # The date is at date_idx, so numbers start at date_idx + 1
            # Expected: اوج بار, اوج بار جمعه, راکتیو, میان باری, کم باری, مبلغ دوره ریال
            number_parts = parts[date_idx + 1:]
            
            # #region agent log
            debug_log("restructure_consumption_history_template5.py:115", "Number parts after date", {"number_parts": number_parts, "number_parts_count": len(number_parts)}, "C")
            # #endregion
            
            all_numbers = []
            for part in number_parts:
                # Remove commas and parse as number
                cleaned = part.replace(',', '')
                if cleaned.isdigit():
                    all_numbers.append(cleaned)
            
            # #region agent log
            debug_log("restructure_consumption_history_template5.py:122", "Extracted numbers", {"all_numbers": all_numbers, "count": len(all_numbers)}, "C")
            # #endregion
            
            if len(all_numbers) >= 6:
                # Standard format with all columns
                # Actual order in text (left to right): اوج بار, اوج بار جمعه, راکتیو, میان باری, کم باری, مبلغ دوره ریال
                # But we need to map to: میان باری, اوج بار, کم باری, اوج بار جمعه, راکتیو, مبلغ دوره ریال
                peak_load = parse_number(all_numbers[0])  # اوج بار (position 0 in text)
                friday_peak = parse_number(all_numbers[1])  # اوج بار جمعه (position 1 in text)
                reactive = parse_number(all_numbers[2])  # راکتیو (position 2 in text)
                mid_load = parse_number(all_numbers[3])  # میان باری (position 3 in text)
                off_peak_load = parse_number(all_numbers[4])  # کم باری (position 4 in text)
                period_amount = parse_number(all_numbers[5])  # مبلغ دوره ریال (position 5 in text)
            elif len(all_numbers) >= 5:
                # Missing one value (likely اوج بار جمعه is 0 or missing)
                peak_load = parse_number(all_numbers[0])  # اوج بار
                friday_peak = 0  # اوج بار جمعه (default to 0)
                reactive = parse_number(all_numbers[1])  # راکتیو
                mid_load = parse_number(all_numbers[2])  # میان باری
                off_peak_load = parse_number(all_numbers[3])  # کم باری
                period_amount = parse_number(all_numbers[4])  # مبلغ دوره ریال
            else:
                # Fallback: try to parse what we can
                peak_load = parse_number(all_numbers[0]) if len(all_numbers) > 0 else None
                friday_peak = parse_number(all_numbers[1]) if len(all_numbers) > 1 else 0
                reactive = parse_number(all_numbers[2]) if len(all_numbers) > 2 else None
                mid_load = parse_number(all_numbers[3]) if len(all_numbers) > 3 else None
                off_peak_load = parse_number(all_numbers[4]) if len(all_numbers) > 4 else None
                period_amount = parse_number(all_numbers[-1]) if len(all_numbers) > 0 else None
            
            # #region agent log
            debug_log("restructure_consumption_history_template5.py:145", "Parsed values before mapping", {
                "peak_load": peak_load,
                "friday_peak": friday_peak,
                "reactive": reactive,
                "mid_load": mid_load,
                "off_peak_load": off_peak_load,
                "period_amount": period_amount,
                "numbers_count": len(all_numbers)
            }, "D")
            # #endregion
            
            row_data = {
                "دوره/سال": period,
                "تاریخ قرائت": reading_date,
                "مصارف کیلووات ساعت": {
                    "میان باری": mid_load,
                    "اوج بار": peak_load,
                    "کم باری": off_peak_load,
                    "اوج بار جمعه": friday_peak,
                    "راکتیو": reactive
                },
                "مبلغ دوره ریال": period_amount,
                "مهلت پرداخت": payment_deadline,
                "مبلغ پرداختی": None,
                "تاریخ پرداخت": payment_date
            }
            
            # #region agent log
            debug_log("restructure_consumption_history_template5.py:165", "Final row_data mapping", {
                "row_data": row_data
            }, "D")
            # #endregion
            
            result["سوابق مصارف مبالغ و پرداختهای ادوار گذشته"]["rows"].append(row_data)
    
    return result


def restructure_consumption_history_template5_json(json_path: Path, output_path: Path):
    """Restructure extracted JSON to include consumption history data for Template 5."""
    print(f"Restructuring Consumption History (Template 5) from {json_path}...")
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        text = data.get('text', '')
        table_data = data.get('table', {})
        
        # Extract consumption history data
        history_data = extract_consumption_history_data(text, table_data)
        
        # Build restructured data
        result = history_data
        
        # Save restructured JSON
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"  - Saved to {output_path}")
        row_count = len(history_data['سوابق مصارف مبالغ و پرداختهای ادوار گذشته']['rows'])
        print(f"  - Extracted {row_count} history rows")
        
        return result
        
    except Exception as e:
        print(f"Error restructuring Consumption History T5: {e}")
        import traceback
        traceback.print_exc()
        return None

