from pathlib import Path
import json
import re
from text_normalization import default_normalizer

def parse_number(text):
    """Parse a number string, removing commas and handling Persian format."""
    if not text:
        return None
    # Remove commas and spaces
    clean = text.replace(',', '').replace(' ', '').strip()
    try:
        return int(clean)
    except ValueError:
        try:
            return float(clean)
        except ValueError:
            return None

def restructure_financial_table_template4_json(json_path: Path, output_path: Path):
    """
    Restructures Financial Table (Template 4).
    
    جدول مالی شامل:
    - مصارف انرژی (میان باری، اوج بار، کم باری، اوج بار جمعه) با مقادیر مصرف، نرخ و بهای انرژی
    - بهای انرژی و سایر هزینه‌ها (بهای انرژی تامین شده، آبونمان، تجاوز از قدرت، و غیره)
    """
    print(f"Restructuring Financial Table (Template 4) from {json_path}...")
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # Don't apply BIDI - it reverses the order of numbers in RTL text
        text = default_normalizer.normalize(data.get("text", ""), apply_bidi=False)
        lines = text.split('\n')
        
        # استخراج جدول مصارف انرژی
        energy_consumptions = []
        
        # الگو برای یافتن ردیف‌های مصرف
        consumption_patterns = {
            "میان_باری": r"میان\s*باری",
            "اوج_بار": r"اوج\s*بار(?!\s*جمعه)",
            "کم_باری": r"کم\s*باری",
            "اوج_بار_جمعه": r"اوج\s*بار\s*جمعه"
        }
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # بررسی هر الگوی مصرف
            for key, pattern in consumption_patterns.items():
                if re.search(pattern, line):
                    # استخراج اعداد از خط
                    numbers = re.findall(r'[\d,]+(?:\.\d+)?', line)
                    # فیلتر اعداد معتبر (حداقل 3 رقم)
                    numbers = [n for n in numbers if re.search(r'\d', n)]
                    
                    if numbers:
                        row = {
                            "نوع_مصرف": key.replace('_', ' '),
                        }
                        
                        # تبدیل اعداد به مقادیر عددی برای بررسی
                        parsed_numbers = [parse_number(n) for n in numbers]
                        
                        # پیدا کردن مصرف: اولین عدد بزرگ (معمولاً > 1000) که می‌تواند مصرف باشد
                        # یا اگر همه اعداد کوچک هستند، از ترتیب استفاده می‌کنیم
                        consumption_value = None
                        consumption_idx = 0
                        
                        # اگر اولین عدد صفر است، به دنبال اولین عدد غیرصفر بزرگ بگرد
                        if parsed_numbers[0] == 0:
                            for idx, num in enumerate(parsed_numbers):
                                if num and num > 1000:  # مصرف معمولاً > 1000 کیلووات ساعت
                                    consumption_value = num
                                    consumption_idx = idx
                                    break
                        
                        # اگر مصرف پیدا نشد، از اولین عدد استفاده کن
                        if consumption_value is None:
                            consumption_value = parsed_numbers[0] if parsed_numbers else 0
                        
                        row["مصرف_کیلووات_ساعت"] = consumption_value
                        
                        # پیدا کردن بهای انرژی: بزرگترین عدد که مصرف نیست
                        energy_price = 0
                        for num in parsed_numbers:
                            if num and num > 100000 and num != consumption_value:
                                energy_price = num
                                break
                        
                        # نرخ‌ها: بعد از مصرف و قبل از بهای انرژی
                        rate_start_idx = consumption_idx + 1
                        row["نرخ_اول"] = 0
                        row["نرخ_دوم"] = 0
                        row["نرخ_سوم"] = 0
                        
                        # استخراج نرخ‌ها: اعداد بین مصرف و بهای انرژی
                        # نرخ‌ها معمولاً کوچکتر از 100,000 هستند
                        rates = []
                        for idx in range(rate_start_idx, len(parsed_numbers)):
                            num = parsed_numbers[idx]
                            # اگر به بهای انرژی رسیدیم، متوقف شو
                            if num == energy_price:
                                break
                            # اگر عدد معتبر است و کوچکتر از 100,000 است، احتمالاً نرخ است
                            if num and num < 100000:
                                rates.append(num)
                        
                        # اختصاص نرخ‌ها
                        if len(rates) >= 1:
                            row["نرخ_اول"] = rates[0]
                        if len(rates) >= 2:
                            row["نرخ_دوم"] = rates[1]
                        if len(rates) >= 3:
                            row["نرخ_سوم"] = rates[2]
                        
                        row["بهای_انرژی_ریال"] = energy_price
                        
                        energy_consumptions.append(row)
                        break  # هر خط فقط یک نوع مصرف دارد
        
        # استخراج بهای انرژی و هزینه‌های دیگر از بخش جدول
        costs = {}
        
        # اگر جدول وجود دارد، از آن استفاده کن
        table_data = data.get("table", {})
        if table_data and "rows" in table_data:
            # جستجوی ردیف با لیست هزینه‌ها
            for row in table_data["rows"]:
                for cell in row:
                    if cell and isinstance(cell, str):
                        # بررسی وجود لیست هزینه‌ها
                        if "بهای انرژی تامین شده:" in cell or "بهای انرژی تامین شده" in cell:
                            # پیدا کردن ردیف مجاور که اعداد دارد
                            row_idx = table_data["rows"].index(row)
                            # جستجوی اعداد در ردیف‌های مجاور
                            for check_row in table_data["rows"][max(0, row_idx-2):row_idx+3]:
                                for check_cell in check_row:
                                    if check_cell and isinstance(check_cell, str):
                                        # اگر شامل اعداد زیادی است (لیست هزینه‌ها)
                                        numbers_in_cell = re.findall(r'-?\d[\d,]*', check_cell)
                                        if len(numbers_in_cell) >= 10:  # لیست هزینه‌ها معمولاً بیشتر از 10 عدد دارد
                                            # تقسیم به خطوط
                                            lines_in_cell = check_cell.split('\n')
                                            # استخراج لیست هزینه‌ها
                                            cost_labels = [
                                                "بهای انرژی تامین شده",
                                                "مابه التفاوت ماده 16 جهش تولید",
                                                "مابه التفاوت اجرای مقررات",
                                                "بهای فصل",
                                                "آبونمان",
                                                "تجاوز از قدرت",
                                                "بهای انرژی راکتیو",
                                                "بستانکاری خرید خارج بازار",
                                                "هزینه سوخت نیروگاهی",
                                                "بهای برق دوره",
                                                "عوارض برق",
                                                "مالیات برارزش افزوده",
                                                "بدهکار/بستانکار",
                                                "کسر هزار ریال"
                                            ]
                                            
                                            # پیدا کردن ردیف با لیست اعداد
                                            numbers_row = None
                                            for num_check_row in table_data["rows"]:
                                                for num_check_cell in num_check_row:
                                                    if num_check_cell and isinstance(num_check_cell, str):
                                                        num_list = re.findall(r'-?\d[\d,]*', num_check_cell)
                                                        if len(num_list) >= 10:
                                                            numbers_row = num_check_cell
                                                            break
                                                if numbers_row:
                                                    break
                                            
                                            if numbers_row:
                                                # تقسیم اعداد
                                                cost_values = re.findall(r'-?\d[\d,]*', numbers_row)
                                                cost_values = [parse_number(v) for v in cost_values]
                                                
                                                # تطبیق برچسب‌ها با مقادیر
                                                for i, label in enumerate(cost_labels):
                                                    if i < len(cost_values) and cost_values[i] is not None:
                                                        costs[label] = cost_values[i]
                                            break
                                        if len(numbers_in_cell) >= 10:
                                            break
                                    if len(check_row) > 0 and isinstance(check_row[0], str) and "بهای انرژی تامین شده:" in check_row[0]:
                                        break
                                if len(check_row) > 0 and isinstance(check_row[0], str) and "بهای انرژی تامین شده:" in check_row[0]:
                                    break
        
        # اگر هزینه‌ها از جدول استخراج نشد، از متن تلاش کن
        if not costs:
            # جستجوی الگوهای هزینه در متن
            full_text = ' '.join(lines)
            
            cost_patterns = {
                "بهای انرژی تامین شده": r"بهای\s*انرژی\s*تامین\s*شده\s*:?\s*(-?\d[\d,]*)",
                "آبونمان": r"آبونمان\s*:?\s*(-?\d[\d,]*)",
                "تجاوز از قدرت": r"تجاوز\s*از\s*قدرت\s*:?\s*(-?\d[\d,]*)",
                "هزینه سوخت نیروگاهی": r"هزینه\s*سوخت\s*نیروگاهی\s*:?\s*(-?\d[\d,]*)",
                "بهای برق دوره": r"بهای\s*برق\s*دوره\s*:?\s*(-?\d[\d,]*)",
                "عوارض برق": r"عوارض\s*برق\s*:?\s*(-?\d[\d,]*)",
                "مالیات برارزش افزوده": r"مالیات\s*برارزش\s*افزوده\s*:?\s*(-?\d[\d,]*)",
            }
            
            for label, pattern in cost_patterns.items():
                match = re.search(pattern, full_text, re.IGNORECASE)
                if match:
                    costs[label] = parse_number(match.group(1))
        
        result = {
            "جدول_مصارف_انرژی": energy_consumptions,
            "هزینه‌ها": costs
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"Extracted {len(energy_consumptions)} consumption rows and {len(costs)} cost items")
            
        return result
    except Exception as e:
        print(f"Error restructuring Financial T4: {e}")
        import traceback
        traceback.print_exc()
        return None