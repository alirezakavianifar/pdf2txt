import sys
import json
import os
import argparse
from pathlib import Path

# Add current directory to path to ensure imports work
sys.path.append(str(Path.cwd()))

from adjust_crop import apply_crop_with_coords
from config import default_config
from extract_text import PDFTextExtractor
from restructure_power_section import restructure_power_section_json
from restructure_consumption_history import restructure_consumption_history_json
from restructure_period_section import restructure_period_section_json
from restructure_period_section_template9 import restructure_period_section_template9_json
from restructure_license_expiry import restructure_license_expiry_json
from restructure_complete import restructure_json
from restructure_bill_summary import restructure_bill_summary_json
from restructure_transit_section import restructure_transit_section_json
from restructure_bill_identifier import restructure_bill_identifier_json
from restructure_energy_supported_template2 import restructure_energy_supported_template2_json
from restructure_power_section_template2 import restructure_power_section_template2_json
from restructure_ghodrat_kilowatt_template2 import restructure_ghodrat_kilowatt_template2_json
from restructure_consumption_history_template2 import restructure_consumption_history_template2_json
from restructure_bill_summary_template2 import (
    restructure_bill_summary_template2_json,
    restructure_bill_summary_template2_from_pdf,
)
from restructure_bill_identifier_template3 import restructure_bill_identifier_template3_json
from restructure_license_expiry_template3 import restructure_license_expiry_template3_json
from restructure_energy_consumption_template3 import restructure_energy_consumption_template3_json
from restructure_power_section_template3 import restructure_power_section_template3_json
from restructure_period_section_template3 import restructure_period_section_template3_json
from restructure_reactive_consumption_template3 import restructure_reactive_consumption_template3_json
from restructure_bill_summary_template3 import restructure_bill_summary_template3_json
from restructure_rate_difference_template3 import restructure_rate_difference_template3_json
from restructure_transit_section_template3 import restructure_transit_section_template3_json
from restructure_power_section_template4 import restructure_power_section_template4_json
from restructure_license_expiry_template4 import restructure_license_expiry_template4_json
from restructure_transformer_coefficient_template4 import restructure_transformer_coefficient_template4_json
from restructure_consumption_table_template4 import restructure_consumption_table_template4_json
from restructure_period_section_template4 import restructure_period_section_template4_json
from restructure_financial_table_template4 import restructure_financial_table_template4_json
from restructure_consumption_history_template4 import restructure_consumption_history_template4_json
from restructure_bill_identifier_template4 import restructure_bill_identifier_template4_json
from restructure_transit_section_template4 import restructure_transit_section_template4_json
from restructure_company_info_template5 import restructure_company_info_template5_json
from restructure_license_expiry_template5 import restructure_license_expiry_template5_json
from restructure_energy_consumption_template5 import restructure_energy_consumption_template5_json
from restructure_power_section_template5 import restructure_power_section_template5_json
from restructure_period_section_template5 import restructure_period_section_template5_json
from restructure_reactive_consumption_template5 import restructure_reactive_consumption_template5_json
from restructure_bill_summary_template5 import restructure_bill_summary_template5_json
from restructure_rate_difference_template5 import restructure_rate_difference_template5_json
from restructure_transit_section_template5 import restructure_transit_section_template5_json
from restructure_consumption_history_template5 import restructure_consumption_history_template5_json
from restructure_license_expiry_template6 import restructure_license_expiry_template6_json
from restructure_energy_consumption_template6 import restructure_energy_consumption_template6_json
from restructure_power_section_template6 import restructure_power_section_template6_json
from restructure_period_section_template6 import restructure_period_section_template6_json
from restructure_bill_summary_template6 import restructure_bill_summary_template6_json, restructure_bill_summary_template6_from_pdf
from restructure_transit_section_template6 import restructure_transit_section_template6_json
from restructure_consumption_history_template6 import restructure_consumption_history_template6_json
from restructure_bill_identifier_template7 import restructure_bill_identifier_template7_json
from restructure_license_expiry_template7 import restructure_license_expiry_template7_json
from restructure_company_info_template7 import restructure_company_info_template7_json
from restructure_energy_consumption_template7 import restructure_energy_consumption_template7_json
from restructure_power_section_template7 import restructure_power_section_template7_json
from restructure_period_section_template7 import restructure_period_section_template7_json
from restructure_bill_summary_template7 import restructure_bill_summary_template7_json
from restructure_consumption_history_template7 import restructure_consumption_history_template7_json
from restructure_transit_section_template7 import restructure_transit_section_template7_json
from restructure_bill_identifier_template8 import restructure_bill_identifier_template8_json
from restructure_license_expiry_template8 import restructure_license_expiry_template8_json
from restructure_energy_consumption_template8 import restructure_energy_consumption_template8_json
from restructure_power_section_template8 import restructure_power_section_template8_json
from restructure_period_section_template8 import restructure_period_section_template8_json
from restructure_consumption_history_template8 import restructure_consumption_history_template8_json
from restructure_bill_summary_template8 import restructure_bill_summary_template8_json
from restructure_transit_section_template8 import restructure_transit_section_template8_json
from restructure_consumption_table_template9 import restructure_consumption_table_template9_json
from restructure_bill_summary_template9 import restructure_bill_summary_template9_json, restructure_bill_summary_template9_from_pdf
from restructure_consumption_history_template9 import restructure_consumption_history_template9_json
from restructure_power_section_template9 import restructure_power_section_template9_json
from pdf_classifier import detect_template
import pandas as pd


def flatten_json_to_row(data: dict, pdf_filename: str, prefix: str = "") -> dict:
    """
    Flatten nested JSON structure into a flat dictionary for Excel row.
    Handles nested dicts (dot notation), arrays (indexed columns), and primitives.
    """
    flat_dict = {}
    
    for key, value in data.items():
        new_key = f"{prefix}.{key}" if prefix else key
        
        if value is None:
            flat_dict[new_key] = ""
        elif isinstance(value, dict):
            # Recursively flatten nested dictionaries
            flat_dict.update(flatten_json_to_row(value, pdf_filename, new_key))
        elif isinstance(value, list):
            # Handle arrays by creating indexed columns
            if len(value) == 0:
                flat_dict[new_key] = ""
            else:
                for idx, item in enumerate(value):
                    if isinstance(item, dict):
                        # If array item is a dict, flatten it with index prefix
                        flat_dict.update(flatten_json_to_row(item, pdf_filename, f"{new_key}_{idx}"))
                    else:
                        # If array item is primitive, just add indexed key
                        flat_dict[f"{new_key}_{idx}"] = item
        else:
            # Primitive value (str, int, float, bool)
            flat_dict[new_key] = value
    
    return flat_dict


def export_to_excel(bills_data: list, output_path: Path):
    """
    Export all bills to a single Excel file.
    
    Args:
        bills_data: List of tuples (pdf_filename, merged_data_dict)
        output_path: Path to output Excel file
    """
    if not bills_data:
        print("No bills data to export to Excel.")
        return
    
    print(f"\n--- Exporting {len(bills_data)} bill(s) to Excel ---")
    
    # Flatten each bill's data
    flattened_rows = []
    for pdf_filename, merged_data in bills_data:
        # Add PDF filename as first column
        flat_row = {"pdf_filename": pdf_filename}
        # Flatten the merged data
        flat_data = flatten_json_to_row(merged_data, pdf_filename)
        flat_row.update(flat_data)
        flattened_rows.append(flat_row)
    
    # Create DataFrame
    df = pd.DataFrame(flattened_rows)
    
    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Write to Excel with proper encoding for Persian/Arabic text
    try:
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Bills')
        
        print(f"  - Excel file saved to: {output_path}")
        print(f"  - Total rows: {len(df)}")
        print(f"  - Total columns: {len(df.columns)}")
    except Exception as e:
        print(f"  - Error exporting to Excel: {e}")
        raise


def export_to_access(bills_data: list, output_path: Path):
    """
    Export all bills to a Microsoft Access database (.accdb file).
    
    Args:
        bills_data: List of tuples (pdf_filename, merged_data_dict)
        output_path: Path to output Access database file
    """
    try:
        import pyodbc
    except ImportError:
        raise ImportError(
            "pyodbc is required for Access export. Install it with: pip install pyodbc\n"
            "Note: Microsoft Access Database Engine (ACE driver) must be installed on Windows."
        )
    
    if not bills_data:
        print("No bills data to export to Access.")
        return
    
    print(f"\n--- Exporting {len(bills_data)} bill(s) to Access ---")
    
    # Flatten each bill's data
    flattened_rows = []
    for pdf_filename, merged_data in bills_data:
        # Add PDF filename as first column
        flat_row = {"pdf_filename": pdf_filename}
        # Flatten the merged data
        flat_data = flatten_json_to_row(merged_data, pdf_filename)
        flat_row.update(flat_data)
        flattened_rows.append(flat_row)
    
    # Create DataFrame
    df = pd.DataFrame(flattened_rows)
    
    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Check if database exists, delete it if it does
    if output_path.exists():
        try:
            output_path.unlink()
        except Exception as e:
            print(f"  - Warning: Could not delete existing database: {e}")
    
    # Find available Access driver
    try:
        available_drivers = pyodbc.drivers()
    except:
        available_drivers = []
    
    drivers_to_try = [
        "Microsoft Access Driver (*.mdb, *.accdb)",
        "Microsoft Access Driver (*.mdb)",
    ]
    
    available_driver = None
    for driver in drivers_to_try:
        if driver in available_drivers:
            available_driver = driver
            break
    
    if not available_driver:
        raise RuntimeError(
            "Microsoft Access Database Engine (ACE driver) not found.\n"
            "Please install it from: https://www.microsoft.com/en-us/download/details.aspx?id=54920\n"
            "After installation, restart the application."
        )
    
    # Create connection string for Access database
    conn_str = f"Driver={{{available_driver}}};DBQ={output_path};"
    
    # Create database using ADO (ActiveX Data Objects) - works with ACE driver only
    # This doesn't require full Microsoft Access installation
    database_created = False
    try:
        import win32com.client
        
        # Convert path to absolute and ensure it's a string
        db_path = str(output_path.absolute())
        
        try:
            # Method 1: Try using ADO to create database (works with ACE driver)
            cat = win32com.client.Dispatch("ADOX.Catalog")
            # Use ACE provider connection string
            provider = "Provider=Microsoft.ACE.OLEDB.16.0;"
            # If 16.0 doesn't work, try 12.0
            try:
                cat.Create(f"{provider}Data Source={db_path};")
            except:
                provider = "Provider=Microsoft.ACE.OLEDB.12.0;"
                cat.Create(f"{provider}Data Source={db_path};")
            cat = None
            database_created = True
            print(f"  - Created new Access database using ADO: {db_path}")
        except Exception as ado_error:
            # Method 2: Try using Access.Application (requires full Access)
            try:
                access_app = win32com.client.Dispatch("Access.Application")
                access_app.Visible = False
                access_app.NewCurrentDatabase(db_path)
                access_app.Quit()
                del access_app
                database_created = True
                print(f"  - Created new Access database using Access.Application: {db_path}")
            except Exception as access_error:
                # Both methods failed
                error_msg = str(ado_error)
                raise RuntimeError(
                    f"Failed to create Access database.\n"
                    f"ADO Error: {error_msg}\n"
                    f"Access Error: {str(access_error)}\n\n"
                    "Please ensure one of the following is installed:\n"
                    "1. Microsoft Access Database Engine (ACE driver) - Recommended\n"
                    "   Download: https://www.microsoft.com/en-us/download/details.aspx?id=54920\n"
                    "2. Microsoft Access (full version)\n\n"
                    "Or create an empty .accdb file manually at:\n"
                    f"{db_path}"
                )
    except ImportError:
        # pywin32 not available - cannot create database automatically
        raise RuntimeError(
            "Cannot create Access database automatically. pywin32 is required.\n\n"
            "Please install pywin32:\n"
            "pip install pywin32\n\n"
            "Or create an empty Access database (.accdb) file manually at:\n"
            f"{output_path.absolute()}\n\n"
            "Then run the export again."
        )
    
    # Verify database was created
    if not database_created or not output_path.exists():
        raise RuntimeError(
            "Failed to create Access database. Please ensure:\n"
            "1. Microsoft Access or Access Database Engine is installed\n"
            "2. pywin32 is installed: pip install pywin32\n"
            "3. Or create an empty .accdb file manually"
        )
    
    # Verify we can connect to the newly created database
    try:
        test_conn = pyodbc.connect(conn_str)
        test_conn.close()
    except pyodbc.Error as conn_error:
        raise RuntimeError(
            f"Created database but cannot connect to it: {str(conn_error)}\n\n"
            "Please ensure Microsoft Access Database Engine (ACE driver) is installed.\n"
            "Download from: https://www.microsoft.com/en-us/download/details.aspx?id=54920"
        )
    
    # Create database and table
    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        
        # Drop table if it exists
        try:
            cursor.execute("DROP TABLE Bills")
            conn.commit()
        except pyodbc.Error:
            pass  # Table doesn't exist, that's fine
        
        # Create table with all columns
        # Access has limitations on column names and types
        # We'll use TEXT for all columns to handle Persian/Arabic text
        columns = []
        for col in df.columns:
            # Clean column name (Access doesn't like certain characters)
            clean_col = col.replace(".", "_").replace(" ", "_").replace("-", "_")
            # Limit column name length (Access max is 64 chars)
            if len(clean_col) > 64:
                clean_col = clean_col[:64]
            columns.append(f"[{clean_col}] TEXT(255)")
        
        create_table_sql = f"CREATE TABLE Bills ({', '.join(columns)})"
        cursor.execute(create_table_sql)
        conn.commit()
        
        # Insert data row by row
        for _, row in df.iterrows():
            # Prepare values, handling None and special characters
            values = []
            placeholders = []
            for col in df.columns:
                clean_col = col.replace(".", "_").replace(" ", "_").replace("-", "_")
                if len(clean_col) > 64:
                    clean_col = clean_col[:64]
                
                value = row[col]
                if pd.isna(value) or value is None:
                    values.append(None)
                else:
                    # Convert to string and handle encoding
                    str_value = str(value)
                    values.append(str_value)
                placeholders.append("?")
            
            # Build insert statement
            clean_cols = [col.replace(".", "_").replace(" ", "_").replace("-", "_")[:64] for col in df.columns]
            insert_sql = f"INSERT INTO Bills ([{'], ['.join(clean_cols)}]) VALUES ({', '.join(placeholders)})"
            cursor.execute(insert_sql, values)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"  - Access database saved to: {output_path}")
        print(f"  - Total rows: {len(df)}")
        print(f"  - Total columns: {len(df.columns)}")
        
    except pyodbc.Error as e:
        error_msg = str(e)
        if "Microsoft Access Driver" in error_msg or "ACE" in error_msg or "driver" in error_msg.lower():
            raise RuntimeError(
                f"Access database driver not found. Please install Microsoft Access Database Engine (ACE driver).\n"
                f"Download from: https://www.microsoft.com/en-us/download/details.aspx?id=54920\n"
                f"Error: {error_msg}"
            )
        else:
            raise RuntimeError(f"Error exporting to Access: {error_msg}")
    except Exception as e:
        print(f"  - Error exporting to Access: {e}")
        raise


def run_pipeline(pdf_filename="1.pdf", export_excel=False):
    print(f"\n--- Starting Full Pipeline for {pdf_filename} ---\n")
    
    # 0. Resolve Input Path
    # Handle paths with spaces and special characters
    input_path = Path(pdf_filename)

    # Directory mode: process all PDFs directly under the given folder (non-recursive),
    # to avoid picking up already-cropped section PDFs in subfolders.
    if input_path.exists() and input_path.is_dir():
        pdf_files = sorted([p for p in input_path.glob("*.pdf") if p.is_file()])
        if not pdf_files:
            print(f"Error: No PDF files found in directory: {input_path}")
            return

        print(f"Found {len(pdf_files)} PDF(s) in: {input_path}")
        errors = 0
        bills_data = []  # Collect data for Excel export
        
        for i, pdf_file in enumerate(pdf_files, start=1):
            try:
                print(f"\n[{i}/{len(pdf_files)}] {pdf_file.name}")
                merged_data = run_pipeline(str(pdf_file), export_excel=False)
                if merged_data and export_excel:
                    bills_data.append((pdf_file.name, merged_data))
            except Exception as e:
                errors += 1
                print(f"[ERROR] Failed processing {pdf_file.name}: {e}")

        print(f"\nBatch complete: {len(pdf_files) - errors} succeeded, {errors} failed")
        
        # Export all bills to Excel if requested
        if export_excel and bills_data:
            output_root = Path("output")
            excel_path = output_root / "bills_export.xlsx"
            export_to_excel(bills_data, excel_path)
        
        return

    input_pdf = input_path
    
    # If path doesn't exist, try as absolute path first
    if not input_pdf.exists():
        # Try as absolute path if it looks like a full path
        if os.path.isabs(pdf_filename):
            input_pdf = Path(pdf_filename)
        else:
            # Try relative to current directory
            input_pdf = Path.cwd() / pdf_filename
    
    # If still doesn't exist, try fallback to template1 folder
    if not input_pdf.exists():
        # Only use template1 fallback if filename doesn't contain a path separator
        if os.sep not in pdf_filename and '/' not in pdf_filename:
            input_pdf = Path("template1") / pdf_filename
        else:
            # If it contains path separators, try relative to current directory
            input_pdf = Path.cwd() / pdf_filename
        
    if not input_pdf.exists():
        print(f"Error: {input_pdf} not found")
        print(f"  Searched for: {pdf_filename}")
        print(f"  Current directory: {Path.cwd()}")
        return

    # 1. Classification
    print(f"1. Classifying {input_pdf.name}...")
    template_id = "template_1"
    confidence = 0.0
    details = {}
    try:
        template_id, confidence, details = detect_template(input_pdf)
        print(f"   Detected: {template_id} (Confidence: {confidence:.2f})")
        
        # Check if template matches configuration (currently hardcoded for template 1)
        if template_id not in ["template_1", "template1"]:
            print(f"   WARNING: Detected {template_id}, but pipeline is currently valid for Template 1.")
            print("   Proceeding, but cropping configuration might not match.")
            
    except Exception as e:
        print(f"   Classification failed: {e}")
        # Proceed anyway? Or return? Lets proceed as fallback
        
    # Put all JSON outputs for this PDF under: output/<pdf_stem>/
    output_root = Path("output")
    output_dir = output_root / input_pdf.stem
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Branch based on template
    merged_data = None
    if template_id in ["template_1", "template1"]:
        merged_data = process_template_1(input_pdf, output_dir, template_id, confidence)
    elif template_id in ["template_2", "template2"]:
        merged_data = process_template_2(input_pdf, output_dir, template_id, confidence)
    elif template_id in ["template_3", "template3"]:
        merged_data = process_template_3(input_pdf, output_dir, template_id, confidence)
    elif template_id in ["template_4", "template4"]:
        merged_data = process_template_4(input_pdf, output_dir, template_id, confidence)
    elif template_id in ["template_5", "template5"]:
        merged_data = process_template_5(input_pdf, output_dir, template_id, confidence)
    elif template_id in ["template_6", "template6"]:
        merged_data = process_template_6(input_pdf, output_dir, template_id, confidence)
    elif template_id in ["template_7", "template7"]:
        merged_data = process_template_7(input_pdf, output_dir, template_id, confidence)
    elif template_id in ["template_8", "template8"]:
        merged_data = process_template_8(input_pdf, output_dir, template_id, confidence)
    elif template_id in ["template_9", "template9"]:
        merged_data = process_template_9(input_pdf, output_dir, template_id, confidence)
    else:
        print(f"   WARNING: Unknown template {template_id}. Defaulting to Template 1 logic.")
        merged_data = process_template_1(input_pdf, output_dir, template_id, confidence)

    print("\n--- Pipeline Complete ---")
    
    # Export to Excel if requested (single PDF mode)
    if export_excel and merged_data:
        output_root = Path("output")
        excel_path = output_root / "bills_export.xlsx"
        export_to_excel([(input_pdf.name, merged_data)], excel_path)
    
    return merged_data


def process_template_1(input_pdf, output_dir, template_id="template_1", confidence=1.0):
    """
    Process PDF using Template 1 logic (cropping and specific restructuring)
    """
    print(f"\n[Template 1 Process] Starting for {input_pdf.name}...")
    
    # 2. Crop
    print(f"2. Cropping {input_pdf.name} into sections...")
    cropped_files = []
    cropped_dir = output_dir / "cropped"
    
    for section in default_config.crop.sections:
        name = section['name']
        coords = (section['x0'], section['y0'], section['x1'], section['y1'])
        
        # apply_crop_with_coords(x0, y0, x1, y1, input_pdf, output_pdf=None, section_name="cropped")
        success, result, size, out_path = apply_crop_with_coords(
            *coords, 
            str(input_pdf), 
            section_name=name,
            output_base_dir=cropped_dir
        )
        
        if success:
            print(f"  - Cropped {name}: {out_path}")
            cropped_files.append((name, Path(out_path)))
        else:
            print(f"  - Failed to crop {name}: {result}")

    # 3. Extract & Restructure
    print(f"\n3. Extracting and Restructuring...")
    extractor = PDFTextExtractor()
    merged_data = {
        "classification": {
            "template_id": template_id,
            "confidence": confidence
        }
    }
    intermediate_files = [] # Track files to clean up
    
    for name, pdf_path in cropped_files:
        print(f"\n  Processing {name}...")
        
        # Extract
        results = extractor.extract_all(str(pdf_path))
        base_name = f"{input_pdf.stem}_{name}"
        
        # Save raw
        extractor.save_results(results, output_dir, base_name)
        json_path = output_dir / f"{base_name}.json"
        intermediate_files.append(json_path)
        
        # Restructure
        restructured_path = output_dir / f"{base_name}_restructured.json"
        intermediate_files.append(restructured_path)
        
        try:
            data = None
            if name == "power_section":
                data = restructure_power_section_json(json_path, restructured_path)
            elif name == "period_section":
                data = restructure_period_section_json(json_path, restructured_path)
            elif name == "consumption_history_section":
                data = restructure_consumption_history_json(json_path, restructured_path)
            elif name == "license_expiry_section":
                data = restructure_license_expiry_json(json_path, restructured_path)
            elif name == "energy_supported_section":
                data = restructure_json(json_path, restructured_path)
            elif name == "bill_summary_section":
                data = restructure_bill_summary_json(json_path, restructured_path)
            elif name == "transit_section":
                data = restructure_transit_section_json(json_path, restructured_path)
            elif name == "bill_identifier_section":
                data = restructure_bill_identifier_json(json_path, restructured_path)
            else:
                print(f"    Warning: No restructure script for {name}")
                
            if data:
                merged_data.update(data)
                
        except Exception as e:
            try:
                print(f"    Error restructuring {name}: {e}")
            except UnicodeEncodeError:
                print(f"    Error restructuring {name}: {str(e).encode('ascii', 'replace').decode('ascii')}")

    # 4. Save Final
    print(f"\n4. Saving Final Combined Output...")
    final_path = output_dir / f"{input_pdf.stem}_final_pipeline.json"
    
    with open(final_path, 'w', encoding='utf-8') as f:
        json.dump(merged_data, f, ensure_ascii=False, indent=2)
        
    print(f"  - Saved to {final_path}")
    print(f"  - Merged {len(merged_data)} sections/keys")
    
    # 5. Cleanup
    # 5. Cleanup
    print("\n5. Cleanup skipped (Debugging enabled)...")
    # for f_path in intermediate_files:
    #     try:
    #         if f_path.exists():
    #             f_path.unlink()
    #     except Exception as e:
    #         print(f"  Warning: Could not delete {f_path.name}: {e}")
    
    return merged_data


def process_template_2(input_pdf, output_dir, template_id="template_2", confidence=1.0):
    """
    Process PDF using Template 2 logic
    """
    print(f"\n[Template 2 Process] Starting for {input_pdf.name}...")
    
    # 2. Crop
    print(f"2. Cropping {input_pdf.name} into sections (Template 2)...")
    cropped_files = []
    cropped_dir = output_dir / "cropped"
    
    # Use Template 2 specific sections
    sections = default_config.crop.sections_template_2
    
    for section in sections:
        name = section['name']
        coords = (section['x0'], section['y0'], section['x1'], section['y1'])
        
        success, result, size, out_path = apply_crop_with_coords(
            *coords, 
            str(input_pdf), 
            section_name=name,
            output_base_dir=cropped_dir
        )
        
        if success:
            print(f"  - Cropped {name}: {out_path}")
            cropped_files.append((name, Path(out_path)))
        else:
            print(f"  - Failed to crop {name}: {result}")

    # 3. Extract & Restructure
    print(f"\n3. Extracting and Restructuring...")
    extractor = PDFTextExtractor()
    merged_data = {
        "classification": {
            "template_id": template_id,
            "confidence": confidence
        }
    }
    intermediate_files = [] # Track files to clean up
    
    for name, pdf_path in cropped_files:
        print(f"\n  Processing {name}...")
        
        # Extract
        results = extractor.extract_all(str(pdf_path))
        base_name = f"{input_pdf.stem}_{name}"
        
        # Save raw
        extractor.save_results(results, output_dir, base_name)
        json_path = output_dir / f"{base_name}.json"
        intermediate_files.append(json_path)
        
        # Restructure
        restructured_path = output_dir / f"{base_name}_restructured.json"
        intermediate_files.append(restructured_path)
        
        try:
            data = None
            # Map sections to their restructure functions
            # Assuming widely shared logic; if specific logic is needed, create new restructure scripts
            if name == "power_section":
                # Template 2 uses dedicated restructuring for power section
                data = restructure_power_section_template2_json(json_path, restructured_path)
            elif name == "period_section":
                data = restructure_period_section_json(json_path, restructured_path)
            elif name == "license_expiry_section":
                data = restructure_license_expiry_json(json_path, restructured_path)
            elif name == "energy_supported_section":
                # Template 2 uses dedicated restructuring for energy section
                data = restructure_energy_supported_template2_json(json_path, restructured_path)
            elif name == "bill_identifier_section":
                data = restructure_bill_identifier_json(json_path, restructured_path)
            elif name == "bill_summary_section":
                # Template 2 uses strip-based extraction directly from the cropped PDF
                data = restructure_bill_summary_template2_from_pdf(str(pdf_path), restructured_path)
            elif name == "consumption_history_section":
                # Template 2 uses dedicated restructuring for consumption history section
                data = restructure_consumption_history_template2_json(json_path, restructured_path)
            elif name == "ghodrat_kilowatt_section":
                # Template 2 uses dedicated restructuring for ghodrat_kilowatt section
                data = restructure_ghodrat_kilowatt_template2_json(json_path, restructured_path)
            else:
                print(f"    Warning: No restructure script for {name}")
                
            if data:
                merged_data.update(data)
                
        except Exception as e:
            try:
                print(f"    Error restructuring {name}: {e}")
            except UnicodeEncodeError:
                print(f"    Error restructuring {name}: {str(e).encode('ascii', 'replace').decode('ascii')}")

    # 4. Save Final
    print(f"\n4. Saving Final Combined Output...")
    final_path = output_dir / f"{input_pdf.stem}_final_pipeline.json"
    
    with open(final_path, 'w', encoding='utf-8') as f:
        json.dump(merged_data, f, ensure_ascii=False, indent=2)
        
    print(f"  - Saved to {final_path}")
    print(f"  - Merged {len(merged_data)} sections/keys")
    
    # 5. Cleanup
    print("\n5. Cleanup skipped (Debugging enabled)...")
    # for f_path in intermediate_files:
    #     try:
    #         if f_path.exists():
    #             f_path.unlink()
    #     except Exception as e:
    #         print(f"  Warning: Could not delete {f_path.name}: {e}")
    
    return merged_data


def process_template_3(input_pdf, output_dir, template_id="template_3", confidence=1.0):
    """
    Process PDF using Template 3 logic
    """
    print(f"\n[Template 3 Process] Starting for {input_pdf.name}...")
    
    # 2. Crop
    print(f"2. Cropping {input_pdf.name} into sections (Template 3)...")
    cropped_files = []
    cropped_dir = output_dir / "cropped"
    
    # Use Template 3 specific sections
    sections = default_config.crop.sections_template_3
    
    for section in sections:
        name = section['name']
        coords = (section['x0'], section['y0'], section['x1'], section['y1'])
        
        success, result, size, out_path = apply_crop_with_coords(
            *coords, 
            str(input_pdf), 
            section_name=name,
            output_base_dir=cropped_dir
        )
        
        if success:
            print(f"  - Cropped {name}: {out_path}")
            cropped_files.append((name, Path(out_path)))
        else:
            print(f"  - Failed to crop {name}: {result}")

    # 3. Extract & Restructure
    print(f"\n3. Extracting and Restructuring...")
    extractor = PDFTextExtractor()
    merged_data = {
        "classification": {
            "template_id": template_id,
            "confidence": confidence
        }
    }
    intermediate_files = [] # Track files to clean up
    
    for name, pdf_path in cropped_files:
        print(f"\n  Processing {name}...")
        
        # Extract
        results = extractor.extract_all(str(pdf_path))
        base_name = f"{input_pdf.stem}_{name}"
        
        # Save raw
        extractor.save_results(results, output_dir, base_name)
        json_path = output_dir / f"{base_name}.json"
        intermediate_files.append(json_path)
        
        # Restructure
        restructured_path = output_dir / f"{base_name}_restructured.json"
        intermediate_files.append(restructured_path)
        
        try:
            data = None
            # Map sections to their restructure functions for Template 3
            if name == "bill_identifier_section":
                data = restructure_bill_identifier_template3_json(json_path, restructured_path)
            elif name == "license_expiry_section":
                data = restructure_license_expiry_template3_json(json_path, restructured_path)
            elif name == "energy_consumption_table_section":
                data = restructure_energy_consumption_template3_json(json_path, restructured_path)
            elif name == "power_section":
                data = restructure_power_section_template3_json(json_path, restructured_path)
            elif name == "period_section":
                data = restructure_period_section_template3_json(json_path, restructured_path)
            elif name == "reactive_consumption_section":
                data = restructure_reactive_consumption_template3_json(json_path, restructured_path)
            elif name == "bill_summary_section":
                data = restructure_bill_summary_template3_json(json_path, restructured_path)
            elif name == "rate_difference_table_section":
                data = restructure_rate_difference_template3_json(json_path, restructured_path)
            elif name == "transit_section":
                data = restructure_transit_section_template3_json(json_path, restructured_path)
            else:
                print(f"    Warning: No restructure script for {name}")
                
            if data:
                merged_data.update(data)
                
        except Exception as e:
            try:
                print(f"    Error restructuring {name}: {e}")
            except UnicodeEncodeError:
                print(f"    Error restructuring {name}: {str(e).encode('ascii', 'replace').decode('ascii')}")

    # 4. Save Final
    print(f"\n4. Saving Final Combined Output...")
    final_path = output_dir / f"{input_pdf.stem}_final_pipeline.json"
    
    with open(final_path, 'w', encoding='utf-8') as f:
        json.dump(merged_data, f, ensure_ascii=False, indent=2)
        
    print(f"  - Saved to {final_path}")
    print(f"  - Merged {len(merged_data)} sections/keys")
    
    # 5. Cleanup
    print("\n5. Cleanup skipped (Debugging enabled)...")
    # for f_path in intermediate_files:
    #     try:
    #         if f_path.exists():
    #             f_path.unlink()
    #     except Exception as e:
    #         print(f"  Warning: Could not delete {f_path.name}: {e}")
    
    return merged_data

def process_template_4(input_pdf, output_dir, template_id="template_4", confidence=1.0):
    """
    Process PDF using Template 4 logic
    """
    print(f"\n[Template 4 Process] Starting for {input_pdf.name}...")
    
    # 2. Crop
    print(f"2. Cropping {input_pdf.name} into sections (Template 4)...")
    cropped_files = []
    cropped_dir = output_dir / "cropped"
    
    # Use Template 4 specific sections
    sections = default_config.crop.sections_template_4
    
    for section in sections:
        name = section['name']
        coords = (section['x0'], section['y0'], section['x1'], section['y1'])
        
        success, result, size, out_path = apply_crop_with_coords(
            *coords, 
            str(input_pdf), 
            section_name=name,
            output_base_dir=cropped_dir
        )
        
        if success:
            print(f"  - Cropped {name}: {out_path}")
            cropped_files.append((name, Path(out_path)))
        else:
            print(f"  - Failed to crop {name}: {result}")

    # 3. Extract & Restructure
    print(f"\n3. Extracting and Restructuring...")
    extractor = PDFTextExtractor()
    merged_data = {
        "classification": {
            "template_id": template_id,
            "confidence": confidence
        }
    }
    
    for name, pdf_path in cropped_files:
        print(f"\n  Processing {name}...")
        
        # Extract
        results = extractor.extract_all(str(pdf_path))
        base_name = f"{input_pdf.stem}_{name}"
        
        # Save raw
        extractor.save_results(results, output_dir, base_name)
        json_path = output_dir / f"{base_name}.json"
        
        # Restructure
        restructured_path = output_dir / f"{base_name}_restructured.json"
        
        try:
            data = None
            if name == "power_section":
                data = restructure_power_section_template4_json(json_path, restructured_path)
            elif name == "license_expiry_section":
                data = restructure_license_expiry_template4_json(json_path, restructured_path)
            elif name == "transformer_coefficient_section":
                data = restructure_transformer_coefficient_template4_json(json_path, restructured_path)
            elif name == "consumption_table_section":
                data = restructure_consumption_table_template4_json(json_path, restructured_path)
            elif name == "period_section":
                data = restructure_period_section_template4_json(json_path, restructured_path)
            elif name == "financial_table_section":
                data = restructure_financial_table_template4_json(json_path, restructured_path)
            elif name == "consumption_history_section":
                data = restructure_consumption_history_template4_json(json_path, restructured_path)
            elif name == "bill_identifier_section":
                data = restructure_bill_identifier_template4_json(json_path, restructured_path)
            elif name == "transit_section":
                data = restructure_transit_section_template4_json(json_path, restructured_path)
            else:
                print(f"    Warning: No restructure script for {name}")
                
            if data:
                merged_data.update(data)
                
        except Exception as e:
            try:
                print(f"    Error restructuring {name}: {e}")
            except UnicodeEncodeError:
                print(f"    Error restructuring {name}: {str(e).encode('ascii', 'replace').decode('ascii')}")

    # 4. Save Final
    print(f"\n4. Saving Final Combined Output...")
    final_path = output_dir / f"{input_pdf.stem}_final_pipeline.json"
    
    with open(final_path, 'w', encoding='utf-8') as f:
        json.dump(merged_data, f, ensure_ascii=False, indent=2)
        
    print(f"  - Saved to {final_path}")
    print(f"  - Merged {len(merged_data)} sections/keys")
    
    # 5. Cleanup
    print("\n5. Cleanup skipped (Debugging enabled)...")
    
    return merged_data


def process_template_5(input_pdf, output_dir, template_id="template_5", confidence=1.0):
    """
    Process PDF using Template 5 logic
    """
    print(f"\n[Template 5 Process] Starting for {input_pdf.name}...")
    
    # 2. Crop
    print(f"2. Cropping {input_pdf.name} into sections (Template 5)...")
    cropped_files = []
    cropped_dir = output_dir / "cropped"
    
    # Use Template 5 specific sections
    sections = default_config.crop.sections_template_5
    
    for section in sections:
        name = section['name']
        coords = (section['x0'], section['y0'], section['x1'], section['y1'])
        
        success, result, size, out_path = apply_crop_with_coords(
            *coords, 
            str(input_pdf), 
            section_name=name,
            output_base_dir=cropped_dir
        )
        
        if success:
            print(f"  - Cropped {name}: {out_path}")
            cropped_files.append((name, Path(out_path)))
        else:
            print(f"  - Failed to crop {name}: {result}")

    # 3. Extract & Restructure
    print(f"\n3. Extracting and Restructuring...")
    extractor = PDFTextExtractor()
    merged_data = {
        "classification": {
            "template_id": template_id,
            "confidence": confidence
        }
    }
    intermediate_files = [] # Track files to clean up
    
    for name, pdf_path in cropped_files:
        print(f"\n  Processing {name}...")
        
        # Extract
        results = extractor.extract_all(str(pdf_path))
        base_name = f"{input_pdf.stem}_{name}"
        
        # Save raw
        extractor.save_results(results, output_dir, base_name)
        json_path = output_dir / f"{base_name}.json"
        intermediate_files.append(json_path)
        
        # Restructure
        restructured_path = output_dir / f"{base_name}_restructured.json"
        intermediate_files.append(restructured_path)
        
        try:
            data = None
            # Map sections to their restructure functions for Template 5
            if name == "company_info_section":
                data = restructure_company_info_template5_json(json_path, restructured_path)
            elif name == "license_expiry_section":
                data = restructure_license_expiry_template5_json(json_path, restructured_path)
            elif name == "energy_consumption_table_section":
                data = restructure_energy_consumption_template5_json(json_path, restructured_path)
            elif name == "power_section":
                data = restructure_power_section_template5_json(json_path, restructured_path)
            elif name == "period_section":
                data = restructure_period_section_template5_json(json_path, restructured_path)
            elif name == "reactive_consumption_section":
                data = restructure_reactive_consumption_template5_json(json_path, restructured_path)
            elif name == "bill_summary_section":
                data = restructure_bill_summary_template5_json(json_path, restructured_path)
            elif name == "rate_difference_table_section":
                data = restructure_rate_difference_template5_json(json_path, restructured_path)
            elif name == "transit_section":
                data = restructure_transit_section_template5_json(json_path, restructured_path)
            elif name == "consumption_history_section":
                data = restructure_consumption_history_template5_json(json_path, restructured_path)
            else:
                print(f"    Warning: No restructure script for {name}")
                
            if data:
                merged_data.update(data)
                
        except Exception as e:
            try:
                print(f"    Error restructuring {name}: {e}")
            except UnicodeEncodeError:
                print(f"    Error restructuring {name}: {str(e).encode('ascii', 'replace').decode('ascii')}")

    # 4. Save Final
    print(f"\n4. Saving Final Combined Output...")
    final_path = output_dir / f"{input_pdf.stem}_final_pipeline.json"
    
    with open(final_path, 'w', encoding='utf-8') as f:
        json.dump(merged_data, f, ensure_ascii=False, indent=2)
        
    print(f"  - Saved to {final_path}")
    print(f"  - Merged {len(merged_data)} sections/keys")
    
    # 5. Cleanup
    print("\n5. Cleanup skipped (Debugging enabled)...")
    
    return merged_data


def process_template_6(input_pdf, output_dir, template_id="template_6", confidence=1.0):
    """
    Process PDF using Template 6 logic
    """
    print(f"\n[Template 6 Process] Starting for {input_pdf.name}...")
    
    # 2. Crop
    print(f"2. Cropping {input_pdf.name} into sections (Template 6)...")
    cropped_files = []
    cropped_dir = output_dir / "cropped"
    
    # Use Template 6 specific sections
    sections = default_config.crop.sections_template_6
    
    for section in sections:
        name = section['name']
        coords = (section['x0'], section['y0'], section['x1'], section['y1'])
        
        success, result, size, out_path = apply_crop_with_coords(
            *coords, 
            str(input_pdf), 
            section_name=name,
            output_base_dir=cropped_dir
        )
        
        if success:
            print(f"  - Cropped {name}: {out_path}")
            cropped_files.append((name, Path(out_path)))
        else:
            print(f"  - Failed to crop {name}: {result}")

    # 3. Extract & Restructure
    print(f"\n3. Extracting and Restructuring...")
    extractor = PDFTextExtractor()
    merged_data = {
        "classification": {
            "template_id": template_id,
            "confidence": confidence
        }
    }
    intermediate_files = [] # Track files to clean up
    
    for name, pdf_path in cropped_files:
        print(f"\n  Processing {name}...")
        
        # Extract
        results = extractor.extract_all(str(pdf_path))
        base_name = f"{input_pdf.stem}_{name}"
        
        # Save raw
        extractor.save_results(results, output_dir, base_name)
        json_path = output_dir / f"{base_name}.json"
        intermediate_files.append(json_path)
        
        # Restructure
        restructured_path = output_dir / f"{base_name}_restructured.json"
        intermediate_files.append(restructured_path)
        
        try:
            data = None
            # Map sections to their restructure functions for Template 6
            if name == "license_expiry_section":
                data = restructure_license_expiry_template6_json(json_path, restructured_path)
            elif name == "energy_consumption_table_section":
                data = restructure_energy_consumption_template6_json(json_path, restructured_path)
            elif name == "power_section":
                data = restructure_power_section_template6_json(json_path, restructured_path)
            elif name == "period_section":
                data = restructure_period_section_template6_json(json_path, restructured_path)
            elif name == "bill_summary_section":
                # Template 6 uses strip-based extraction directly from the cropped PDF
                # This avoids text contamination issues from overlapping PDF layers
                data = restructure_bill_summary_template6_from_pdf(str(pdf_path), restructured_path)
            elif name == "transit_section":
                data = restructure_transit_section_template6_json(json_path, restructured_path)
            elif name == "consumption_history_section":
                data = restructure_consumption_history_template6_json(json_path, restructured_path)
            else:
                print(f"    Warning: No restructure script for {name}")
                
            if data:
                merged_data.update(data)
                
        except Exception as e:
            try:
                print(f"    Error restructuring {name}: {e}")
            except UnicodeEncodeError:
                print(f"    Error restructuring {name}: {str(e).encode('ascii', 'replace').decode('ascii')}")

    # 4. Save Final
    print(f"\n4. Saving Final Combined Output...")
    final_path = output_dir / f"{input_pdf.stem}_final_pipeline.json"
    
    with open(final_path, 'w', encoding='utf-8') as f:
        json.dump(merged_data, f, ensure_ascii=False, indent=2)
        
    print(f"  - Saved to {final_path}")
    print(f"  - Merged {len(merged_data)} sections/keys")
    
    # 5. Cleanup
    print("\n5. Cleanup skipped (Debugging enabled)...")
    
    return merged_data


def process_template_7(input_pdf, output_dir, template_id="template_7", confidence=1.0):
    """
    Process PDF using Template 7 logic
    """
    print(f"\n[Template 7 Process] Starting for {input_pdf.name}...")
    
    # 2. Crop
    print(f"2. Cropping {input_pdf.name} into sections (Template 7)...")
    cropped_files = []
    cropped_dir = output_dir / "cropped"
    
    # Use Template 7 specific sections
    sections = default_config.crop.sections_template_7
    
    for section in sections:
        name = section['name']
        coords = (section['x0'], section['y0'], section['x1'], section['y1'])
        
        success, result, size, out_path = apply_crop_with_coords(
            *coords, 
            str(input_pdf), 
            section_name=name,
            output_base_dir=cropped_dir
        )
        
        if success:
            print(f"  - Cropped {name}: {out_path}")
            cropped_files.append((name, Path(out_path)))
        else:
            print(f"  - Failed to crop {name}: {result}")

    # 3. Extract & Restructure
    print(f"\n3. Extracting and Restructuring...")
    extractor = PDFTextExtractor()
    merged_data = {
        "classification": {
            "template_id": template_id,
            "confidence": confidence
        }
    }
    intermediate_files = [] # Track files to clean up
    
    for name, pdf_path in cropped_files:
        print(f"\n  Processing {name}...")
        
        # Extract
        results = extractor.extract_all(str(pdf_path))
        base_name = f"{input_pdf.stem}_{name}"
        
        # Save raw
        extractor.save_results(results, output_dir, base_name)
        json_path = output_dir / f"{base_name}.json"
        intermediate_files.append(json_path)
        
        # Restructure
        restructured_path = output_dir / f"{base_name}_restructured.json"
        intermediate_files.append(restructured_path)
        
        try:
            data = None
            # Map sections to their restructure functions for Template 7
            if name == "bill_identifier_section":
                data = restructure_bill_identifier_template7_json(json_path, restructured_path)
            elif name == "license_expiry_section":
                data = restructure_license_expiry_template7_json(json_path, restructured_path)
            elif name == "company_info_section":
                data = restructure_company_info_template7_json(json_path, restructured_path)
            elif name == "energy_consumption_table_section":
                data = restructure_energy_consumption_template7_json(json_path, restructured_path)
            elif name == "power_section":
                data = restructure_power_section_template7_json(json_path, restructured_path)
            elif name == "period_section":
                data = restructure_period_section_template7_json(json_path, restructured_path)
            elif name == "bill_summary_section":
                data = restructure_bill_summary_template7_json(json_path, restructured_path)
            elif name == "consumption_history_section":
                data = restructure_consumption_history_template7_json(json_path, restructured_path)
            elif name == "transit_section":
                data = restructure_transit_section_template7_json(json_path, restructured_path)
            else:
                print(f"    Warning: No restructure script for {name}")
                
            if data:
                merged_data.update(data)
                
        except Exception as e:
            try:
                print(f"    Error restructuring {name}: {e}")
            except UnicodeEncodeError:
                print(f"    Error restructuring {name}: {str(e).encode('ascii', 'replace').decode('ascii')}")

    # 4. Save Final
    print(f"\n4. Saving Final Combined Output...")
    final_path = output_dir / f"{input_pdf.stem}_final_pipeline.json"
    
    with open(final_path, 'w', encoding='utf-8') as f:
        json.dump(merged_data, f, ensure_ascii=False, indent=2)
        
    print(f"  - Saved to {final_path}")
    print(f"  - Merged {len(merged_data)} sections/keys")
    
    # 5. Cleanup
    print("\n5. Cleanup skipped (Debugging enabled)...")
    # for f_path in intermediate_files:
    #     try:
    #         if f_path.exists():
    #             f_path.unlink()
    #     except Exception as e:
    #         print(f"  Warning: Could not delete {f_path.name}: {e}")

    return merged_data


def process_template_8(input_pdf, output_dir, template_id="template_8", confidence=1.0):
    """
    Process PDF using Template 8 logic
    """
    print(f"\n[Template 8 Process] Starting for {input_pdf.name}...")
    
    # 2. Crop
    print(f"2. Cropping {input_pdf.name} into sections (Template 8)...")
    cropped_files = []
    cropped_dir = output_dir / "cropped"
    
    # Use Template 8 specific sections
    sections = default_config.crop.sections_template_8
    
    for section in sections:
        name = section['name']
        coords = (section['x0'], section['y0'], section['x1'], section['y1'])
        
        success, result, size, out_path = apply_crop_with_coords(
            *coords, 
            str(input_pdf), 
            section_name=name,
            output_base_dir=cropped_dir
        )
        
        if success:
            print(f"  - Cropped {name}: {out_path}")
            cropped_files.append((name, Path(out_path)))
        else:
            print(f"  - Failed to crop {name}: {result}")

    # 3. Extract & Restructure
    print(f"\n3. Extracting and Restructuring...")
    extractor = PDFTextExtractor()
    merged_data = {
        "classification": {
            "template_id": template_id,
            "confidence": confidence
        }
    }
    intermediate_files = [] # Track files to clean up
    
    for name, pdf_path in cropped_files:
        print(f"\n  Processing {name}...")
        
        # Extract
        results = extractor.extract_all(str(pdf_path))
        base_name = f"{input_pdf.stem}_{name}"
        
        # Save raw
        extractor.save_results(results, output_dir, base_name)
        json_path = output_dir / f"{base_name}.json"
        intermediate_files.append(json_path)
        
        # Restructure
        restructured_path = output_dir / f"{base_name}_restructured.json"
        intermediate_files.append(restructured_path)
        
        try:
            data = None
            # Map sections to their restructure functions for Template 8
            if name == "bill_identifier_section":
                data = restructure_bill_identifier_template8_json(json_path, restructured_path)
            elif name == "license_expiry_section":
                data = restructure_license_expiry_template8_json(json_path, restructured_path)
            elif name == "energy_consumption_table_section":
                data = restructure_energy_consumption_template8_json(json_path, restructured_path)
            elif name == "power_section":
                data = restructure_power_section_template8_json(json_path, restructured_path)
            elif name == "period_section":
                data = restructure_period_section_template8_json(json_path, restructured_path)
            elif name == "consumption_history_section":
                data = restructure_consumption_history_template8_json(json_path, restructured_path)
            elif name == "bill_summary_section":
                data = restructure_bill_summary_template8_json(json_path, restructured_path)
            elif name == "transit_section":
                data = restructure_transit_section_template8_json(json_path, restructured_path)
            else:
                print(f"    Warning: No restructure script for {name}")
                
            if data:
                merged_data.update(data)
                
        except Exception as e:
            try:
                print(f"    Error restructuring {name}: {e}")
            except UnicodeEncodeError:
                print(f"    Error restructuring {name}: {str(e).encode('ascii', 'replace').decode('ascii')}")

    # 4. Save Final
    print(f"\n4. Saving Final Combined Output...")
    final_path = output_dir / f"{input_pdf.stem}_final_pipeline.json"
    
    with open(final_path, 'w', encoding='utf-8') as f:
        json.dump(merged_data, f, ensure_ascii=False, indent=2)
        
    print(f"  - Saved to {final_path}")
    print(f"  - Merged {len(merged_data)} sections/keys")
    
    # 5. Cleanup
    print("\n5. Cleanup skipped (Debugging enabled)...")
    # for f_path in intermediate_files:
    #     try:
    #         if f_path.exists():
    #             f_path.unlink()
    #     except Exception as e:
    #         print(f"  Warning: Could not delete {f_path.name}: {e}")
    
    return merged_data


def process_template_9(input_pdf, output_dir, template_id="template_9", confidence=1.0):
    """
    Process PDF using Template 9 logic
    """
    print(f"\n[Template 9 Process] Starting for {input_pdf.name}...")
    
    # 2. Crop
    print(f"2. Cropping {input_pdf.name} into sections (Template 9)...")
    cropped_files = []
    cropped_dir = output_dir / "cropped"
    
    # Use Template 9 specific sections
    sections = default_config.crop.sections_template_9
    
    for section in sections:
        name = section['name']
        coords = (section['x0'], section['y0'], section['x1'], section['y1'])
        
        success, result, size, out_path = apply_crop_with_coords(
            *coords, 
            str(input_pdf), 
            section_name=name,
            output_base_dir=cropped_dir
        )
        
        if success:
            print(f"  - Cropped {name}: {out_path}")
            cropped_files.append((name, Path(out_path)))
        else:
            print(f"  - Failed to crop {name}: {result}")

    # 3. Extract & Restructure
    print(f"\n3. Extracting and Restructuring...")
    extractor = PDFTextExtractor()
    merged_data = {
        "classification": {
            "template_id": template_id,
            "confidence": confidence
        }
    }
    intermediate_files = [] # Track files to clean up
    
    for name, pdf_path in cropped_files:
        print(f"\n  Processing {name}...")
        
        # Extract
        results = extractor.extract_all(str(pdf_path))
        base_name = f"{input_pdf.stem}_{name}"
        
        # Save raw
        extractor.save_results(results, output_dir, base_name)
        json_path = output_dir / f"{base_name}.json"
        intermediate_files.append(json_path)
        
        # Restructure
        restructured_path = output_dir / f"{base_name}_restructured.json"
        intermediate_files.append(restructured_path)
        
        try:
            data = None
            # Map sections to their restructure functions for Template 9
            if name == "bill_identifier_section":
                data = restructure_bill_identifier_json(json_path, restructured_path)
            elif name == "license_expiry_section":
                data = restructure_license_expiry_json(json_path, restructured_path)
            elif name == "consumption_table_section":
                data = restructure_consumption_table_template9_json(json_path, restructured_path)
            elif name == "period_section":
                data = restructure_period_section_template9_json(json_path, restructured_path)
            elif name == "power_section":
                data = restructure_power_section_template9_json(json_path, restructured_path)
            elif name == "bill_summary_section":
                # Template 9: Try JSON-based parsing first, fallback to strip-based if needed
                try:
                    data = restructure_bill_summary_template9_json(json_path, restructured_path)
                    # If JSON parsing extracted few fields, try strip-based as fallback
                    if data and "خلاصه صورتحساب" in data:
                        extracted_count = sum(1 for v in data["خلاصه صورتحساب"].values() if v is not None)
                        if extracted_count < 3:
                            print(f"    JSON parsing extracted only {extracted_count} fields, trying strip-based extraction...")
                            data = restructure_bill_summary_template9_from_pdf(str(pdf_path), restructured_path)
                except Exception as e:
                    print(f"    JSON parsing failed: {e}, trying strip-based extraction...")
                    data = restructure_bill_summary_template9_from_pdf(str(pdf_path), restructured_path)
            elif name == "consumption_history_section":
                data = restructure_consumption_history_template9_json(json_path, restructured_path)
            else:
                print(f"    Warning: No restructure script for {name}")
                
            if data:
                merged_data.update(data)
                
        except Exception as e:
            try:
                print(f"    Error restructuring {name}: {e}")
            except UnicodeEncodeError:
                print(f"    Error restructuring {name}: {str(e).encode('ascii', 'replace').decode('ascii')}")

    # Post-processing: Calculate missing fields from other sections for Template 9
    # Calculate "مبلغ مصرف" from consumption table if missing
    if "خلاصه صورتحساب" in merged_data and merged_data["خلاصه صورتحساب"].get("مبلغ مصرف") is None:
        if "consumption_table_section" in merged_data and "rows" in merged_data["consumption_table_section"]:
            total_consumption_amount = 0
            for row in merged_data["consumption_table_section"]["rows"]:
                if "مبلغ" in row and row["مبلغ"] is not None:
                    try:
                        total_consumption_amount += float(row["مبلغ"])
                    except (ValueError, TypeError):
                        pass
            if total_consumption_amount > 0:
                merged_data["خلاصه صورتحساب"]["مبلغ مصرف"] = total_consumption_amount

    # 4. Save Final
    print(f"\n4. Saving Final Combined Output...")
    final_path = output_dir / f"{input_pdf.stem}_final_pipeline.json"
    
    with open(final_path, 'w', encoding='utf-8') as f:
        json.dump(merged_data, f, ensure_ascii=False, indent=2)
        
    print(f"  - Saved to {final_path}")
    print(f"  - Merged {len(merged_data)} sections/keys")
    
    # 5. Cleanup
    print("\n5. Cleanup skipped (Debugging enabled)...")
    # for f_path in intermediate_files:
    #     try:
    #         if f_path.exists():
    #             f_path.unlink()
    #     except Exception as e:
    #         print(f"  Warning: Could not delete {f_path.name}: {e}")
    
    return merged_data


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Process PDF files and extract structured data",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "pdf_filename",
        nargs="?",
        default="1.pdf",
        help="PDF file or directory to process (default: 1.pdf)"
    )
    parser.add_argument(
        "--excel",
        action="store_true",
        help="Export all processed bills to Excel file (output/bills_export.xlsx)"
    )
    
    args = parser.parse_args()
    run_pipeline(args.pdf_filename, export_excel=args.excel)
