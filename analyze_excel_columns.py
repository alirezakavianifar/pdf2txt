"""
Analyze Excel export to identify common columns across templates.
This script examines the bills_export.xlsx file to find column patterns.
"""
import pandas as pd
from pathlib import Path
from collections import defaultdict
import re

def analyze_excel_columns(excel_path):
    """Analyze columns in the Excel file to identify patterns."""
    try:
        df = pd.read_excel(excel_path)
        print(f"Total columns: {len(df.columns)}")
        print(f"Total rows: {len(df)}")
        print("\n" + "="*80)
        
        # Group columns by their base name (before template suffix)
        column_groups = defaultdict(list)
        
        for col in df.columns:
            # Check if column has a template-specific suffix pattern
            # Pattern: base_name.field_name or just field_name
            
            # Remove template-specific suffixes if present
            base_col = col
            
            # Try to identify template-specific patterns
            # e.g., "classification.template_id" -> "classification"
            if '.' in col:
                parts = col.split('.')
                # Check if any part contains template info
                base_col = col
            
            column_groups[base_col].append(col)
        
        # Identify truly common columns (appear in all rows with data)
        print("\n=== Column Analysis ===\n")
        
        # Analyze each column
        for col in sorted(df.columns):
            non_null_count = df[col].notna().sum()
            if non_null_count > 0:
                print(f"{col}")
                print(f"  Non-null values: {non_null_count}/{len(df)}")
                print(f"  Sample values: {df[col].dropna().head(2).tolist()}")
                print()
        
        # Identify potential common field patterns
        print("\n=== Potential Common Fields ===\n")
        
        # Look for fields that appear across multiple templates
        # by analyzing the column name structure
        field_patterns = defaultdict(list)
        
        for col in df.columns:
            # Extract the last part of dotted notation (actual field name)
            if '.' in col:
                field_name = col.split('.')[-1]
                field_patterns[field_name].append(col)
            else:
                field_patterns[col].append(col)
        
        # Show fields that appear multiple times (likely common across templates)
        for field_name, columns in sorted(field_patterns.items()):
            if len(columns) > 1:
                print(f"\nField '{field_name}' appears in {len(columns)} columns:")
                for col in columns:
                    print(f"  - {col}")
        
        return df, column_groups, field_patterns
        
    except Exception as e:
        print(f"Error analyzing Excel file: {e}")
        import traceback
        traceback.print_exc()
        return None, None, None

if __name__ == "__main__":
    excel_path = Path("dist/bills_export.xlsx")
    
    if not excel_path.exists():
        print(f"Error: {excel_path} not found")
        print("Please run the pipeline with Excel export first to generate the file.")
    else:
        df, column_groups, field_patterns = analyze_excel_columns(excel_path)
