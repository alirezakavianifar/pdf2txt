
import re

def parse_decimal_number(text):
    if not text:
        return None
    clean_text = text.replace(',', '')
    if '/' in clean_text and len(clean_text) < 10:
        clean_text = clean_text.replace('/', '.')
    try:
        return float(clean_text)
    except ValueError:
        return None

line = "22.4 778 - قدرت مشمول ترانزیت کسر هزار ریال"
normalized_line = line.strip()

print(f"Line: {line}")

# Original Regex
nums_orig = re.findall(r'[\d,]+', normalized_line)
print(f"Original Regex nums: {nums_orig}")

# Proposed Regex
nums_new = re.findall(r'[\d,.]+', normalized_line)
print(f"New Regex nums: {nums_new}")

# Logic simulation
result = {"اطلاعات ترانزیت": {"قدرت مشمول ترانزیت": None, "کسر هزار ریال": None}}
key = "کسر هزار ریال"

# Simulate finding Power first?
# The loop order in main script depends on dictionary order.
# But assuming Power is None initially.

nums = [n for n in nums_new if re.match(r'^[\d,.]+$', n) and '/' not in n] # Fixed regex in filtering too
print(f"Filtered nums: {nums}")

if len(nums) >= 2:
    if result["اطلاعات ترانزیت"]["قدرت مشمول ترانزیت"]:
        power_val = result["اطلاعات ترانزیت"]["قدرت مشمول ترانزیت"]
        for n in nums:
             n_val = parse_decimal_number(n)
             if n_val != power_val:
                 print(f"Selected (Power Known): {n_val}")
                 break
    else:
        # Power unknown.
        # Current bad logic: picks nums[0] -> 22.4
        print(f"Selected (Power Unknown - Current Logic): {parse_decimal_number(nums[0])}")
        
        # Better logic? 
        # Usually 'KSr Hezar Rial' (Thousand Deduction) is the integer, and smaller? 
        # Or maybe specifically the second number?
        # In this specific text layout: "22.4 778 - ..."
        # 22.4 is Power. 778 is Deduction.
        # So picking the last one properly?
        print(f"Selected (Power Unknown - Last One): {parse_decimal_number(nums[-1])}")
