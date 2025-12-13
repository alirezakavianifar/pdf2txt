"""
Main pipeline script for extracting text from PDFs.
Processes cropped PDFs and extracts text, tables, and geometry.
"""
import json
import csv
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
import pdfplumber
import pandas as pd
from config import PDF2TextConfig, default_config
from text_normalization import TextNormalizer, default_normalizer
from geometry_extraction import GeometryExtractor, default_extractor


class PDFTextExtractor:
    """Main class for extracting text from PDFs."""
    
    def __init__(self, config: PDF2TextConfig = None):
        """
        Initialize PDF text extractor.
        
        Args:
            config: Configuration object (uses default if None)
        """
        self.config = config or default_config
        self.normalizer = TextNormalizer(
            normalize_whitespace=self.config.normalization.normalize_whitespace,
            remove_extra_spaces=self.config.normalization.remove_extra_spaces,
            normalize_persian_numbers=self.config.normalization.normalize_persian_numbers,
            handle_bidi=self.config.normalization.handle_bidi
        )
        self.geometry_extractor = GeometryExtractor(
            extract_cell_bounds=self.config.geometry.extract_cell_bounds,
            extract_table_structure=self.config.geometry.extract_table_structure,
            min_cell_width=self.config.geometry.min_cell_width,
            min_cell_height=self.config.geometry.min_cell_height
        )
    
    def extract_text(self, pdf_path: str, page_num: int = 0, crop_bbox: Optional[Tuple[float, float, float, float]] = None) -> str:
        """
        Extract plain text from PDF page, optionally within a crop region.
        
        Args:
            pdf_path: Path to PDF file
            page_num: Page number (0-indexed)
            crop_bbox: Optional (x0, y0, x1, y1) bounding box to extract from
        
        Returns:
            Extracted and normalized text
        """
        try:
            with pdfplumber.open(pdf_path) as pdf:
                if page_num >= len(pdf.pages):
                    return ""
                
                page = pdf.pages[page_num]
                
                # If crop box is specified, extract only from that region
                if crop_bbox:
                    x0, y0, x1, y1 = crop_bbox
                    # Extract words and filter by coordinates (strict filtering)
                    words = page.extract_words()
                    filtered_words = [
                        w for w in words
                        if (x0 <= w["x0"] and w["x1"] <= x1 and
                            y0 <= w["top"] and w["bottom"] <= y1)
                    ]
                    
                    if filtered_words:
                        # Reconstruct text from filtered words
                        # Sort by top (y) then left (x) for proper reading order
                        filtered_words.sort(key=lambda w: (w["top"], w["x0"]))
                        text_lines = []
                        current_line = []
                        current_y = None
                        
                        for word in filtered_words:
                            # Group words on same line (within 5 points vertically)
                            if current_y is None or abs(word["top"] - current_y) > 5:
                                if current_line:
                                    text_lines.append(" ".join(current_line))
                                current_line = [word["text"]]
                                current_y = word["top"]
                            else:
                                # Add space between words if they're not adjacent
                                if current_line and word["x0"] > filtered_words[filtered_words.index(word)-1]["x1"] + 2:
                                    current_line.append(" ")
                                current_line.append(word["text"])
                        
                        if current_line:
                            text_lines.append(" ".join(current_line))
                        
                        text = "\n".join(text_lines)
                    else:
                        text = ""
                else:
                    # Extract text - pdfplumber handles encoding automatically
                    text = page.extract_text()
                
                if not text and not crop_bbox:
                    # Fallback: try extracting with layout preservation
                    text = page.extract_text(layout=True)
                
                if text:
                    # Normalize text with BIDI to convert visual-order to logical-order
                    # This fixes the garbled appearance of RTL text
                    normalized = self.normalizer.normalize(text, apply_bidi=True)
                    return normalized
                return ""
        
        except Exception as e:
            print(f"Error extracting text from {pdf_path}: {e}")
            return ""
    
    def extract_table(self, pdf_path: str, page_num: int = 0, crop_bbox: Optional[Tuple[float, float, float, float]] = None) -> Optional[pd.DataFrame]:
        """
        Extract table from PDF page, optionally within a crop region.
        
        Args:
            pdf_path: Path to PDF file
            page_num: Page number (0-indexed)
            crop_bbox: Optional (x0, y0, x1, y1) bounding box to extract from
        
        Returns:
            DataFrame with table data or None
        """
        try:
            with pdfplumber.open(pdf_path) as pdf:
                if page_num >= len(pdf.pages):
                    return None
                
                page = pdf.pages[page_num]
                
                # Extract tables - but we need to filter by coordinates
                # pdfplumber doesn't respect crop box, so we'll extract and filter
                tables = page.extract_tables()
                
                if not tables:
                    return None
                
                # Use first table
                table = tables[0]
                
                # If crop box specified, filter table cells by their actual positions
                if crop_bbox:
                    x0, y0, x1, y1 = crop_bbox
                    # Get words with positions to map text to coordinates
                    words = page.extract_words()
                    # Create a set of words that are definitely in crop region
                    words_in_crop = {
                        (w["text"].strip(), w["top"], w["x0"])
                        for w in words
                        if (x0 <= w["x0"] and w["x1"] <= x1 and
                            y0 <= w["top"] and w["bottom"] <= y1)
                    }
                    
                    # Extract words for each cell to check if cell is in crop
                    # We'll use a simpler approach: filter rows based on whether
                    # they contain any words that are in the crop region
                    words_in_crop_text_set = {w[0] for w in words_in_crop if len(w[0]) > 2}
                    
                    filtered_table = []
                    for row in table:
                        filtered_row = []
                        row_has_crop_content = False
                        
                        for cell in row:
                            cell_text = str(cell).strip() if cell else ""
                            
                            if cell_text:
                                # Check if cell contains words that are in crop region
                                # Split into meaningful words (length > 2 to avoid noise)
                                cell_words = [w.strip() for w in cell_text.split() if len(w.strip()) > 2]
                                
                                # Check if any significant word from cell is in crop region
                                cell_in_crop = any(
                                    word in words_in_crop_text_set 
                                    for word in cell_words
                                )
                                
                                # Also check for address/name keywords - exclude these
                                has_address_keywords = any(
                                    kw in cell_text 
                                    for kw in ["کاربری", "مشترک محترم", "آدرس", "نشانی محل", 
                                              "کد پستی", "شناسه ملی", "کد اقتصادی", "نشانی محل مکاتباتی"]
                                )
                                
                                if cell_in_crop and not has_address_keywords:
                                    row_has_crop_content = True
                                    filtered_row.append(cell_text)
                                else:
                                    filtered_row.append("")
                            else:
                                filtered_row.append("")
                        
                        # Only add row if it has valid content in crop region
                        if row_has_crop_content:
                            filtered_table.append(filtered_row)
                    
                    # Use filtered table
                    if filtered_table:
                        table = filtered_table
                    else:
                        # If filtering removed everything, return None
                        return None
                
                # Normalize cell text with BIDI to fix character order
                normalized_table = []
                for row in table:
                    normalized_row = []
                    for cell in row:
                        cell_text = str(cell) if cell else ""
                        if cell_text:
                            # Apply BIDI to fix visual-order to logical-order
                            cell_text = self.normalizer.normalize(cell_text, apply_bidi=True).strip()
                        normalized_row.append(cell_text)
                    normalized_table.append(normalized_row)
                
                # Create DataFrame
                if normalized_table:
                    headers = normalized_table[0] if normalized_table else None
                    if headers:
                        # Handle duplicate column names
                        seen = {}
                        unique_headers = []
                        for h in headers:
                            if h in seen:
                                seen[h] += 1
                                unique_headers.append(f"{h}_{seen[h]}")
                            else:
                                seen[h] = 0
                                unique_headers.append(h)
                        headers = unique_headers
                    df = pd.DataFrame(normalized_table[1:], columns=headers)
                    return df
                
                return None
        
        except Exception as e:
            print(f"Error extracting table from {pdf_path}: {e}")
            return None
    
    def get_crop_box_from_pdf(self, pdf_path: str, page_num: int = 0) -> Optional[Tuple[float, float, float, float]]:
        """
        Get crop box coordinates from PDF.
        
        Args:
            pdf_path: Path to PDF file
            page_num: Page number (0-indexed)
        
        Returns:
            (x0, y0, x1, y1) crop box or None
        """
        try:
            import fitz
            doc = fitz.open(pdf_path)
            if page_num >= len(doc):
                doc.close()
                return None
            page = doc[page_num]
            crop = page.cropbox
            media = page.mediabox
            
            # If crop box is different from media box, use crop box
            if crop != media:
                doc.close()
                return (crop.x0, crop.y0, crop.x1, crop.y1)
            
            doc.close()
            return None
        except Exception:
            return None
    
    def extract_all(self, pdf_path: str, page_num: int = 0) -> Dict[str, Any]:
        """
        Extract all information from PDF: text, table, and geometry.
        Respects crop box if present in PDF.
        
        Args:
            pdf_path: Path to PDF file
            page_num: Page number (0-indexed)
        
        Returns:
            Dictionary with extracted data
        """
        result = {
            "pdf_path": pdf_path,
            "page_num": page_num,
            "text": "",
            "table": None,
            "geometry": None,
            "table_df": None
        }
        
        # Get crop box from PDF (if it was cropped)
        crop_bbox = self.get_crop_box_from_pdf(pdf_path, page_num)
        
        # Extract text (filtered by crop box if present)
        result["text"] = self.extract_text(pdf_path, page_num, crop_bbox=crop_bbox)
        
        # Extract table (filtered by crop box if present)
        if self.config.extraction.extract_tables:
            result["table_df"] = self.extract_table(pdf_path, page_num, crop_bbox=crop_bbox)
            
            # Extract geometry
            if self.config.geometry.extract_table_structure:
                geometry = self.geometry_extractor.extract(pdf_path, page_num, method="pdfplumber")
                if geometry:
                    result["geometry"] = {
                        "num_rows": geometry.num_rows,
                        "num_cols": geometry.num_cols,
                        "bbox": geometry.bbox,
                        "cells": [
                            {
                                "row": cell.row,
                                "col": cell.col,
                                "x0": cell.x0,
                                "y0": cell.y0,
                                "x1": cell.x1,
                                "y1": cell.y1,
                                "text": cell.text
                            }
                            for cell in geometry.cells
                        ]
                    }
        
        return result
    
    def save_results(self, results: Dict[str, Any], output_dir: Path, base_name: str):
        """
        Save extraction results to files.
        
        Args:
            results: Dictionary with extracted data
            output_dir: Output directory
            base_name: Base name for output files
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save text
        if "txt" in self.config.output_formats and results.get("text"):
            txt_path = output_dir / f"{base_name}.txt"
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(results["text"])
            print(f"  Saved text to: {txt_path}")
        
        # Save table as CSV
        if "csv" in self.config.output_formats and results.get("table_df") is not None:
            csv_path = output_dir / f"{base_name}.csv"
            results["table_df"].to_csv(csv_path, index=False, encoding="utf-8-sig")
            print(f"  Saved table to: {csv_path}")
        
        # Save JSON with all data
        if "json" in self.config.output_formats:
            json_path = output_dir / f"{base_name}.json"
            # Build clean JSON structure
            json_data = {
                "source_file": Path(results["pdf_path"]).name,
                "text": results["text"]
            }
            
            # Add table data if available - convert to clean list of lists format
            if results.get("table_df") is not None:
                df = results["table_df"]
                # Convert DataFrame to clean table format
                if not df.empty:
                    json_data["table"] = {
                        "headers": df.columns.tolist(),
                        "rows": df.values.tolist(),
                        "row_count": len(df),
                        "column_count": len(df.columns)
                    }
            
            # Add simplified geometry info (optional - only basic stats)
            if results.get("geometry"):
                geom = results["geometry"]
                json_data["table_info"] = {
                    "rows": geom.get("num_rows", 0),
                    "columns": geom.get("num_cols", 0)
                }
            
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(json_data, f, ensure_ascii=False, indent=2)
            print(f"  Saved JSON to: {json_path.name}")
    
    def process_pdf(self, pdf_path: Path, output_dir: Path):
        """
        Process a single PDF file.
        
        Args:
            pdf_path: Path to PDF file
            output_dir: Output directory
        """
        # Create meaningful output name: {pdf_name}_{section_name}
        # e.g., "1_energy_supported_section.json"
        pdf_folder = pdf_path.parent.name  # e.g., "1" or "4_510_9019722204129"
        section_name = pdf_path.stem       # e.g., "energy_supported_section"
        
        # Combine for unique output name
        output_base_name = f"{pdf_folder}_{section_name}"
        
        print(f"\nProcessing: {pdf_folder}/{pdf_path.name}")
        
        # Extract all data
        results = self.extract_all(str(pdf_path))
        
        # Save results with meaningful name
        self.save_results(results, output_dir, output_base_name)
        
        return results
    
    def process_directory(self, input_dir: Optional[Path] = None, output_dir: Optional[Path] = None):
        """
        Process all PDFs in input directory and subdirectories.
        Supports new folder structure: template1/{pdf_name}/{section_name}.pdf
        
        Args:
            input_dir: Input directory (uses config if None)
            output_dir: Output directory (uses config if None)
        """
        input_dir = input_dir or self.config.input_dir
        output_dir = output_dir or self.config.output_dir
        
        if not input_dir.exists():
            print(f"[ERROR] Input directory not found: {input_dir}")
            return
        
        # Find PDF files in subdirectories (new structure: template1/{pdf_name}/{section}.pdf)
        # ONLY process cropped section PDFs, NOT original PDFs
        pdf_files = []
        
        # Look for PDFs in subdirectories (cropped section PDFs)
        for subdir in input_dir.iterdir():
            if subdir.is_dir() and not subdir.name.startswith('.'):
                subdir_pdfs = list(subdir.glob("*.pdf"))
                pdf_files.extend(subdir_pdfs)
        
        # DO NOT process root directory PDFs - only process cropped sections
        
        # Apply exclude pattern if specified
        if self.config.exclude_pattern:
            from fnmatch import fnmatch
            pdf_files = [f for f in pdf_files if not fnmatch(f.name, self.config.exclude_pattern)]
        
        if not pdf_files:
            print(f"[WARNING] No PDF files found in {input_dir} or subdirectories")
            return
        
        print(f"=" * 70)
        print(f"Processing {len(pdf_files)} PDF section(s) from '{input_dir}'")
        print(f"Output directory: '{output_dir}'")
        print(f"=" * 70)
        
        for pdf_file in sorted(pdf_files):
            try:
                self.process_pdf(pdf_file, output_dir)
            except Exception as e:
                print(f"  [ERROR] Failed to process {pdf_file.name}: {e}")


if __name__ == "__main__":
    # Process cropped PDFs in template1 directory and subdirectories
    extractor = PDFTextExtractor()
    
    # Update config to process section PDFs from subdirectories
    extractor.config.input_dir = Path("template1")
    extractor.config.output_dir = Path("output")
    extractor.config.input_pattern = "*.pdf"  # Process all PDFs in subdirectories
    extractor.config.exclude_pattern = ""  # No exclusions needed (structure handles it)
    extractor.config.output_formats = ["json"]  # Only JSON output
    
    extractor.process_directory()
