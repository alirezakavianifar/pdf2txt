"""Verify if all data from the image is present in the JSON output."""
import json

# Load the JSON
with open('output/1_cropped_test.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

text = data['text']
table_rows = data['table']['rows']

print("=" * 70)
print("VERIFICATION: Checking if all image data is in JSON")
print("=" * 70)

# Store verification results
all_found = True
missing_items = []

# Define expected values from image description
expected_values = {
    # Upper Table - Row 1: میان باری
    'mid_load_tou': '13',
    'mid_load_prev_meter': '1724439',
    'mid_load_curr_meter': '1758899',
    'mid_load_consumption': '34460',
    'mid_load_rate': '4063.462',
    'mid_load_amount': '140026901',
    
    # Upper Table - Row 2: اوج باری
    'peak_load_tou': '2',
    'peak_load_prev_meter': '527231',
    'peak_load_curr_meter': '536473',
    'peak_load_consumption': '9242',
    'peak_load_rate': '4506.294',
    'peak_load_amount': '41647169',
    
    # Upper Table - Row 3: کم باری
    'offpeak_load_tou': '9',
    'offpeak_load_prev_meter': '1232928',
    'offpeak_load_curr_meter': '1257250',
    'offpeak_load_consumption': '24322',
    'offpeak_load_rate': '3718',
    'offpeak_load_amount': '90429196',
    
    # Upper Table - Row 4: اوج بار جمعه
    'friday_prev_meter': '88753',
    'friday_curr_meter': '90562',
    'friday_consumption': '1809',
    'friday_rate': '4506.294',
    'friday_amount': '8151886',
    
    # Upper Table - Row 5: جمع (Total)
    'total_tou': '24',
    'total_consumption': '69833',
    'total_amount': '280255152',
    
    # Lower Table - میان باری
    'mid_load_base_rate': '3477',
    'mid_load_avg_market': '2617.65',
    'mid_load_rate_diff': '859.35',
    'mid_load_diff_amount': '29613201',
    
    # Lower Table - اوج باری
    'peak_load_base_rate': '6954',
    'peak_load_avg_market': '2617.65',
    'peak_load_rate_diff': '4336.35',
    'peak_load_diff_amount': '40076547',
    
    # Lower Table - کم باری
    'offpeak_load_base_rate': '1738.5',
    'offpeak_load_avg_market': '2617.65',
    
    # Lower Table - اوج بار جمعه
    'friday_base_rate': '6954',
    'friday_avg_market': '2617.65',
    'friday_rate_diff': '4336.35',
    'friday_diff_amount': '7844457',
    
    # Additional values
    'renewable_rate': '39039',
    'rate_difference_35562': '35562',
    'demand_consumption': '170',
    'power_factor': '0.9996',
    'reactive_prev_meter': '1317779',
    'reactive_curr_meter': '1319874',
    'reactive_consumption': '2095',
    'rate_48100': '48100',
}

def check_value(name, expected, location='text'):
    """Check if a value exists in text or table."""
    global all_found
    
    # Remove commas from expected for matching
    expected_clean = expected.replace(',', '')
    
    found = False
    where = []
    
    # Check in text
    if expected_clean in text.replace(',', '').replace(' ', ''):
        found = True
        where.append('text')
    
    # Check in table rows (flatten)
    table_text = ' '.join([' '.join(str(cell) if cell else '' for cell in row) for row in table_rows])
    if expected_clean in table_text.replace(',', '').replace(' ', ''):
        found = True
        where.append('table')
    
    if not found:
        all_found = False
        missing_items.append(f"{name}: {expected} (expected)")
        print(f"[X] {name}: {expected} - NOT FOUND")
    else:
        print(f"[OK] {name}: {expected} - Found in {', '.join(where)}")

print("\nChecking Upper Table Data:")
print("-" * 70)
check_value('Mid-load TOU', expected_values['mid_load_tou'])
check_value('Mid-load Previous Meter', expected_values['mid_load_prev_meter'])
check_value('Mid-load Current Meter', expected_values['mid_load_curr_meter'])
check_value('Mid-load Consumption', expected_values['mid_load_consumption'])
check_value('Mid-load Rate', expected_values['mid_load_rate'])
check_value('Mid-load Amount', expected_values['mid_load_amount'])

check_value('Peak-load TOU', expected_values['peak_load_tou'])
check_value('Peak-load Previous Meter', expected_values['peak_load_prev_meter'])
check_value('Peak-load Current Meter', expected_values['peak_load_curr_meter'])
check_value('Peak-load Consumption', expected_values['peak_load_consumption'])
check_value('Peak-load Rate', expected_values['peak_load_rate'])
check_value('Peak-load Amount', expected_values['peak_load_amount'])

check_value('Off-peak TOU', expected_values['offpeak_load_tou'])
check_value('Off-peak Previous Meter', expected_values['offpeak_load_prev_meter'])
check_value('Off-peak Current Meter', expected_values['offpeak_load_curr_meter'])
check_value('Off-peak Consumption', expected_values['offpeak_load_consumption'])
check_value('Off-peak Rate', expected_values['offpeak_load_rate'])
check_value('Off-peak Amount', expected_values['offpeak_load_amount'])

check_value('Friday Previous Meter', expected_values['friday_prev_meter'])
check_value('Friday Current Meter', expected_values['friday_curr_meter'])
check_value('Friday Consumption', expected_values['friday_consumption'])
check_value('Friday Rate', expected_values['friday_rate'])
check_value('Friday Amount', expected_values['friday_amount'])

check_value('Total TOU', expected_values['total_tou'])
check_value('Total Consumption', expected_values['total_consumption'])
check_value('Total Amount', expected_values['total_amount'])

print("\nChecking Lower Table Data:")
print("-" * 70)
check_value('Mid-load Base Rate', expected_values['mid_load_base_rate'])
check_value('Mid-load Avg Market Rate', expected_values['mid_load_avg_market'])
check_value('Mid-load Rate Difference', expected_values['mid_load_rate_diff'])
check_value('Mid-load Difference Amount', expected_values['mid_load_diff_amount'])

check_value('Peak-load Base Rate', expected_values['peak_load_base_rate'])
check_value('Peak-load Avg Market Rate', expected_values['peak_load_avg_market'])
check_value('Peak-load Rate Difference', expected_values['peak_load_rate_diff'])
check_value('Peak-load Difference Amount', expected_values['peak_load_diff_amount'])

check_value('Off-peak Base Rate', expected_values['offpeak_load_base_rate'])
check_value('Off-peak Avg Market Rate', expected_values['offpeak_load_avg_market'])

check_value('Friday Base Rate', expected_values['friday_base_rate'])
check_value('Friday Avg Market Rate', expected_values['friday_avg_market'])
check_value('Friday Rate Difference', expected_values['friday_rate_diff'])
check_value('Friday Difference Amount', expected_values['friday_diff_amount'])

print("\nChecking Additional Values:")
print("-" * 70)
check_value('Renewable Rate', expected_values['renewable_rate'])
check_value('Rate Difference 35562', expected_values['rate_difference_35562'])
check_value('Demand Consumption', expected_values['demand_consumption'])
check_value('Power Factor', expected_values['power_factor'])
check_value('Reactive Previous Meter', expected_values['reactive_prev_meter'])
check_value('Reactive Current Meter', expected_values['reactive_curr_meter'])
check_value('Reactive Consumption', expected_values['reactive_consumption'])
check_value('Rate 48100', expected_values['rate_48100'])

print("\n" + "=" * 70)
if all_found:
    print("[SUCCESS] ALL DATA FROM IMAGE IS PRESENT IN JSON")
else:
    print(f"[FAILED] {len(missing_items)} ITEMS NOT FOUND:")
    for item in missing_items:
        print(f"   - {item}")
print("=" * 70)
