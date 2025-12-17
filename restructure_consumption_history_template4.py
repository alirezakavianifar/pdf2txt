
from pathlib import Path
import json
import re
from text_normalization import default_normalizer

def parse_number(text):
    """Parse a number string, removing commas and handling Persian format."""
    if not text:
        return None
    # Remove commas and spaces
    clean = text.replace(',', '').replace(' ', '')
    try:
        return int(clean)
    except ValueError:
        try:
            return float(clean)
        except ValueError:
            return text

def restructure_consumption_history_template4_json(json_path: Path, output_path: Path):
    """
    Restructures Consumption History (Template 4).
    
    ستون‌های جدول:
    - دوره/سال (تاریخ شروع دوره)
    - میان باری (کیلووات ساعت)
    - اوج بار (کیلووات ساعت)
    - کم باری (کیلووات ساعت)
    - اوج بار جمعه (کیلووات ساعت)
    - راکتیو (کیلووات ساعت)
    - مبلغ دوره (ریال)
    - مهلت پرداخت (تاریخ)
    """
    print(f"Restructuring Consumption History (Template 4) from {json_path}...")
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # Don't apply BIDI - it reverses the order of numbers/dates in RTL text
        text = default_normalizer.normalize(data.get("text", ""), apply_bidi=False)
        lines = text.split('\n')
        
        سوابق = []
        
        # الگوی خط داده: تاریخ شروع + اعداد مصرف + مبلغ + تاریخ پایان
        # مثال: 1403/10/01 840000 120000 504000 0 608000 4,709,150,18 1403/10/21
        date_pattern = r"(\d{4}/\d{2}/\d{2})"
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            dates = re.findall(date_pattern, line)
            
            # اگر دو تاریخ وجود داشته باشد، یک ردیف داده داریم
            if len(dates) >= 2:
                تاریخ_دوره = dates[0]  # اولین تاریخ = دوره/سال
                مهلت_پرداخت = dates[-1]  # آخرین تاریخ = مهلت پرداخت
                
                # حذف تاریخ‌ها از خط و استخراج اعداد
                line_without_dates = line
                for d in dates:
                    line_without_dates = line_without_dates.replace(d, ' ')
                
                # استخراج اعداد (با پشتیبانی از کاما در اعداد بزرگ)
                numbers = re.findall(r'[\d,]+', line_without_dates)
                # فیلتر اعداد معتبر (حداقل 1 رقم)
                numbers = [n for n in numbers if re.search(r'\d', n)]
                
                # ترتیب اعداد در جدول:
                # میان باری، اوج بار، کم باری، اوج بار جمعه، راکتیو، مبلغ دوره
                row = {
                    "دوره_سال": تاریخ_دوره,
                    "مهلت_پرداخت": مهلت_پرداخت,
                }
                
                if len(numbers) >= 1:
                    row["میان_باری"] = parse_number(numbers[0])
                if len(numbers) >= 2:
                    row["اوج_بار"] = parse_number(numbers[1])
                if len(numbers) >= 3:
                    row["کم_باری"] = parse_number(numbers[2])
                if len(numbers) >= 4:
                    row["اوج_بار_جمعه"] = parse_number(numbers[3])
                if len(numbers) >= 5:
                    row["راکتیو"] = parse_number(numbers[4])
                if len(numbers) >= 6:
                    row["مبلغ_دوره_ریال"] = parse_number(numbers[5])
                
                سوابق.append(row)
                
        result = {"سوابق_مصرف": سوابق}
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"Extracted {len(سوابق)} rows from consumption history")
            
        return result
    except Exception as e:
        print(f"Error restructuring History T4: {e}")
        return None
