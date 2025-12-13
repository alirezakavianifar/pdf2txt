import json
from pathlib import Path

output_dir = Path("output")
merged_data = {}

# List of files to merge
files = [
    "1_power_section_restructured.json",
    "1_energy_supported_section_restructured.json",
    "1_consumption_history_section_restructured.json",
    "1_period_section_restructured.json",
    "1_license_expiry_section_restructured.json"
]

for filename in files:
    fpath = output_dir / filename
    if fpath.exists():
        with open(fpath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            merged_data.update(data)
    else:
        print(f"Warning: {filename} not found")

output_path = output_dir / "1_full_data.json"
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(merged_data, f, ensure_ascii=False, indent=2)

print(f"Merged {len(merged_data)} keys into {output_path}")
print(json.dumps(merged_data, ensure_ascii=False, indent=2))
