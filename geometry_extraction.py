"""
Geometry extraction module for extracting table structure and cell boundaries.
"""
import pdfplumber
import pandas as pd
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import fitz  # PyMuPDF


@dataclass
class Cell:
    """Represents a table cell with geometry and content."""
    row: int
    col: int
    x0: float
    y0: float
    x1: float
    y1: float
    text: str = ""
    merged: bool = False
    rowspan: int = 1
    colspan: int = 1


@dataclass
class TableGeometry:
    """Represents extracted table geometry."""
    cells: List[Cell]
    num_rows: int
    num_cols: int
    bbox: Tuple[float, float, float, float]  # (x0, y0, x1, y1)


class GeometryExtractor:
    """Extract table geometry and structure from PDF."""
    
    def __init__(self,
                 extract_cell_bounds: bool = True,
                 extract_table_structure: bool = True,
                 min_cell_width: float = 10.0,
                 min_cell_height: float = 10.0):
        """
        Initialize geometry extractor.
        
        Args:
            extract_cell_bounds: Extract individual cell boundaries
            extract_table_structure: Extract table structure (rows/cols)
            min_cell_width: Minimum cell width to consider
            min_cell_height: Minimum cell height to consider
        """
        self.extract_cell_bounds = extract_cell_bounds
        self.extract_table_structure = extract_table_structure
        self.min_cell_width = min_cell_width
        self.min_cell_height = min_cell_height
    
    def extract_with_pdfplumber(self, pdf_path: str, page_num: int = 0) -> Optional[TableGeometry]:
        """
        Extract table geometry using pdfplumber.
        
        Args:
            pdf_path: Path to PDF file
            page_num: Page number (0-indexed)
        
        Returns:
            TableGeometry object or None if extraction fails
        """
        try:
            with pdfplumber.open(pdf_path) as pdf:
                if page_num >= len(pdf.pages):
                    return None
                
                page = pdf.pages[page_num]
                
                # Try to extract tables
                tables = page.extract_tables()
                
                if not tables:
                    return None
                
                # Use the first table found
                table = tables[0]
                
                # Get table bounding box
                table_bbox = page.find_tables()[0].bbox if page.find_tables() else None
                
                if not table_bbox:
                    # Estimate bbox from words in table area
                    words = page.extract_words()
                    if words:
                        xs = [w["x0"] for w in words]
                        x1s = [w["x1"] for w in words]
                        ys = [w["top"] for w in words]
                        y1s = [w["bottom"] for w in words]
                        table_bbox = (min(xs), min(ys), max(x1s), max(y1s))
                    else:
                        table_bbox = page.bbox
                
                # Extract cells
                cells = []
                num_rows = len(table)
                num_cols = max(len(row) for row in table) if table else 0
                
                if self.extract_cell_bounds and table_bbox:
                    # Estimate cell boundaries
                    x0, y0, x1, y1 = table_bbox
                    cell_width = (x1 - x0) / num_cols if num_cols > 0 else 0
                    cell_height = (y1 - y0) / num_rows if num_rows > 0 else 0
                    
                    for row_idx, row in enumerate(table):
                        for col_idx, cell_text in enumerate(row):
                            if cell_text is None:
                                cell_text = ""
                            
                            cell_x0 = x0 + col_idx * cell_width
                            cell_y0 = y0 + row_idx * cell_height
                            cell_x1 = cell_x0 + cell_width
                            cell_y1 = cell_y0 + cell_height
                            
                            cells.append(Cell(
                                row=row_idx,
                                col=col_idx,
                                x0=cell_x0,
                                y0=cell_y0,
                                x1=cell_x1,
                                y1=cell_y1,
                                text=str(cell_text).strip()
                            ))
                
                return TableGeometry(
                    cells=cells,
                    num_rows=num_rows,
                    num_cols=num_cols,
                    bbox=table_bbox
                )
        
        except Exception as e:
            print(f"Error extracting geometry with pdfplumber: {e}")
            return None
    
    def extract_with_pymupdf(self, pdf_path: str, page_num: int = 0) -> Optional[TableGeometry]:
        """
        Extract table geometry using PyMuPDF.
        
        Args:
            pdf_path: Path to PDF file
            page_num: Page number (0-indexed)
        
        Returns:
            TableGeometry object or None if extraction fails
        """
        try:
            doc = fitz.open(pdf_path)
            if page_num >= len(doc):
                doc.close()
                return None
            
            page = doc[page_num]
            
            # Try to find tables using PyMuPDF's table detection
            try:
                tables = page.find_tables()
                if not tables:
                    doc.close()
                    return None
                
                # Use first table
                table = tables[0]
                
                # Extract cells
                cells = []
                rows = table.extract()
                
                num_rows = len(rows)
                num_cols = max(len(row) for row in rows) if rows else 0
                
                bbox = table.bbox
                
                if self.extract_cell_bounds:
                    # Get cell boundaries from table
                    for row_idx, row in enumerate(rows):
                        for col_idx, cell_text in enumerate(row):
                            if cell_text is None:
                                cell_text = ""
                            
                            # PyMuPDF table extraction provides cell info
                            # Estimate cell bounds
                            x0, y0, x1, y1 = bbox
                            cell_width = (x1 - x0) / num_cols if num_cols > 0 else 0
                            cell_height = (y1 - y0) / num_rows if num_rows > 0 else 0
                            
                            cell_x0 = x0 + col_idx * cell_width
                            cell_y0 = y0 + row_idx * cell_height
                            cell_x1 = cell_x0 + cell_width
                            cell_y1 = cell_y0 + cell_height
                            
                            cells.append(Cell(
                                row=row_idx,
                                col=col_idx,
                                x0=cell_x0,
                                y0=cell_y0,
                                x1=cell_x1,
                                y1=cell_y1,
                                text=str(cell_text).strip()
                            ))
                
                doc.close()
                
                return TableGeometry(
                    cells=cells,
                    num_rows=num_rows,
                    num_cols=num_cols,
                    bbox=bbox
                )
            
            except AttributeError:
                # PyMuPDF version might not have find_tables
                doc.close()
                return None
        
        except Exception as e:
            print(f"Error extracting geometry with PyMuPDF: {e}")
            return None
    
    def extract(self, pdf_path: str, page_num: int = 0, method: str = "pdfplumber") -> Optional[TableGeometry]:
        """
        Extract table geometry using specified method.
        
        Args:
            pdf_path: Path to PDF file
            page_num: Page number (0-indexed)
            method: Extraction method ("pdfplumber" or "pymupdf")
        
        Returns:
            TableGeometry object or None if extraction fails
        """
        if method == "pdfplumber":
            return self.extract_with_pdfplumber(pdf_path, page_num)
        elif method == "pymupdf":
            return self.extract_with_pymupdf(pdf_path, page_num)
        else:
            raise ValueError(f"Unknown method: {method}")
    
    def geometry_to_dataframe(self, geometry: TableGeometry) -> pd.DataFrame:
        """Convert TableGeometry to pandas DataFrame."""
        if not geometry or not geometry.cells:
            return pd.DataFrame()
        
        # Create a matrix to handle the table structure
        max_row = max(cell.row for cell in geometry.cells) if geometry.cells else 0
        max_col = max(cell.col for cell in geometry.cells) if geometry.cells else 0
        
        # Initialize matrix
        matrix = [[""] * (max_col + 1) for _ in range(max_row + 1)]
        
        # Fill matrix with cell text
        for cell in geometry.cells:
            if cell.row <= max_row and cell.col <= max_col:
                matrix[cell.row][cell.col] = cell.text
        
        # Create DataFrame
        df = pd.DataFrame(matrix)
        return df


# Default extractor instance
default_extractor = GeometryExtractor()
