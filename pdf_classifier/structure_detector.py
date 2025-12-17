"""
Structural-Based Detection Module (PRIMARY)

Detects templates based on document structure: pages, tables, sections, layout.
"""

from pathlib import Path
from typing import Dict, Tuple
import numpy as np
import cv2
import fitz  # PyMuPDF
from PIL import Image


def detect_by_structure(
    pdf_path: Path,
    templates_db: Dict
) -> Dict[str, float]:
    """
    Detect template using structural features.
    
    Args:
        pdf_path: Path to PDF file
        templates_db: Templates database with signatures
    
    Returns:
        Dictionary mapping template_id to confidence score
    """
    # Extract structural features from input PDF
    input_structure = extract_structural_features(pdf_path)
    
    if not input_structure:
        return {}
    
    # Early exit: Filter by page count first
    input_page_count = input_structure.get("num_pages", 0)
    
    # Compare with each template
    structure_scores = {}
    
    for template_id, template_sig in templates_db.items():
        template_structure = template_sig.get("signatures", {}).get("structural", {})
        
        if not template_structure:
            continue
        
        # Early exit: Skip if page count doesn't match
        template_page_count = template_structure.get("num_pages", 0)
        if input_page_count != template_page_count:
            structure_scores[template_id] = 0.0
            continue
        
        # Calculate structural similarity
        score = compare_structures(input_structure, template_structure)
        structure_scores[template_id] = score
    
    return structure_scores


def extract_structural_features(pdf_path: Path) -> Dict:
    """
    Extract structural features from PDF.
    
    Returns:
        Dictionary with structural features
    """
    try:
        doc = fitz.open(pdf_path)
        if len(doc) == 0:
            return {}
        
        page = doc[0]
        
        # Get page dimensions
        page_rect = page.rect
        page_width = page_rect.width
        page_height = page_rect.height
        
        # Render page for table detection
        mat = fitz.Matrix(300 / 72, 300 / 72)
        pix = page.get_pixmap(matrix=mat)
        img_array = np.frombuffer(pix.samples, dtype=np.uint8).reshape(
            pix.height, pix.width, pix.n
        )
        
        if pix.n == 4:
            img = Image.fromarray(img_array, 'RGBA').convert('RGB')
        else:
            img = Image.fromarray(img_array, 'RGB')
        
        img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        img_gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
        
        # Extract features
        structure = {
            "num_pages": len(doc),
            "page_dimensions": [int(page_width), int(page_height)],
            "aspect_ratio": float(page_width / page_height),
            "orientation": "portrait" if page_height > page_width else "landscape"
        }
        
        # Detect tables
        tables = detect_tables(img_gray, int(page_width), int(page_height))
        structure["tables"] = tables
        
        # Detect sections
        sections = detect_sections(img_gray, int(page_width), int(page_height))
        structure["sections"] = sections
        
        # Detect layout
        layout = detect_layout(img_gray, int(page_width), int(page_height))
        structure["layout"] = layout
        
        doc.close()
        
        return structure
    except Exception as e:
        print(f"[ERROR] Failed to extract structural features: {e}")
        return {}


def detect_tables(
    img_gray: np.ndarray,
    page_width: int,
    page_height: int
) -> Dict:
    """Detect table structures in the image."""
    # Apply edge detection
    edges = cv2.Canny(img_gray, 50, 150)
    
    # Detect horizontal and vertical lines
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
    vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 40))
    
    horizontal_lines = cv2.morphologyEx(edges, cv2.MORPH_OPEN, horizontal_kernel, iterations=2)
    vertical_lines = cv2.morphologyEx(edges, cv2.MORPH_OPEN, vertical_kernel, iterations=2)
    
    # Count lines (simple approximation)
    h_lines_count = int(np.sum(horizontal_lines > 0) // 1000)
    v_lines_count = int(np.sum(vertical_lines > 0) // 1000)
    
    # Estimate table count
    table_count = max(1, min(h_lines_count, v_lines_count) // 10)
    
    # For main consumption table, estimate rows and columns
    main_table_rows = max(3, h_lines_count // 5)
    main_table_cols = max(3, v_lines_count // 5)
    
    main_table = {
        "rows": int(main_table_rows),
        "cols": int(main_table_cols),
        "bbox_norm": [0.1, 0.25, 0.9, 0.65],  # Default
        "cell_arrangement": f"grid_{int(main_table_rows)}x{int(main_table_cols)}"
    }
    
    return {
        "count": int(table_count),
        "main_consumption": main_table
    }


def detect_sections(
    img_gray: np.ndarray,
    page_width: int,
    page_height: int
) -> Dict:
    """Detect document sections."""
    sections = {
        "header": {
            "present": True,
            "bbox_norm": [0.0, 0.0, 1.0, 0.25]
        },
        "consumption_table": {
            "present": True,
            "bbox_norm": [0.1, 0.25, 0.9, 0.65]
        },
        "payment_info": {
            "present": True,
            "bbox_norm": [0.1, 0.7, 0.9, 0.95]
        }
    }
    
    return sections


def detect_layout(
    img_gray: np.ndarray,
    page_width: int,
    page_height: int
) -> Dict:
    """Detect layout structure."""
    mid_x = page_width // 2
    left_density = np.mean(img_gray[:, :mid_x] < 200)
    right_density = np.mean(img_gray[:, mid_x:] < 200)
    
    if abs(left_density - right_density) < 0.1:
        column_layout = "two_column"
    else:
        column_layout = "single_column"
    
    return {
        "column_layout": column_layout,
        "section_spacing": [0.05, 0.1, 0.15]  # Default
    }


def compare_structures(input_structure: Dict, template_structure: Dict) -> float:
    """
    Compare input structure with template structure.
    
    Returns:
        Similarity score (0.0 to 1.0)
    """
    scores = []
    weights = []
    
    # Page structure matching (20%)
    page_score = compare_page_structure(input_structure, template_structure)
    scores.append(page_score)
    weights.append(0.20)
    
    # Table structure matching (50%)
    table_score = compare_table_structure(input_structure, template_structure)
    scores.append(table_score)
    weights.append(0.50)
    
    # Section matching (25%)
    section_score = compare_sections(input_structure, template_structure)
    scores.append(section_score)
    weights.append(0.25)
    
    # Layout matching (5%)
    layout_score = compare_layout(input_structure, template_structure)
    scores.append(layout_score)
    weights.append(0.05)
    
    # Weighted average
    total_score = sum(s * w for s, w in zip(scores, weights))
    total_weight = sum(weights)
    
    if total_weight > 0:
        return total_score / total_weight
    else:
        return 0.0


def compare_page_structure(input: Dict, template: Dict) -> float:
    """Compare page structure."""
    score = 0.0
    
    # Page count
    if input.get("num_pages") == template.get("num_pages"):
        score += 0.5
    else:
        score += 0.0
    
    # Aspect ratio
    input_ratio = input.get("aspect_ratio", 0)
    template_ratio = template.get("aspect_ratio", 0)
    if input_ratio > 0 and template_ratio > 0:
        ratio_diff = abs(input_ratio - template_ratio) / max(input_ratio, template_ratio)
        score += (1.0 - ratio_diff) * 0.5
    
    return score


def compare_table_structure(input: Dict, template: Dict) -> float:
    """Compare table structure."""
    input_tables = input.get("tables", {})
    template_tables = template.get("tables", {})
    
    score = 0.0
    
    # Table count
    input_count = input_tables.get("count", 0)
    template_count = template_tables.get("count", 0)
    if input_count == template_count:
        score += 0.3
    else:
        # Partial credit for similar counts
        count_diff = abs(input_count - template_count)
        score += max(0.0, 0.3 - count_diff * 0.1)
    
    # Main table structure
    input_main = input_tables.get("main_consumption", {})
    template_main = template_tables.get("main_consumption", {})
    
    # Rows
    input_rows = input_main.get("rows", 0)
    template_rows = template_main.get("rows", 0)
    if input_rows == template_rows:
        score += 0.35
    else:
        row_diff = abs(input_rows - template_rows)
        max_rows = max(input_rows, template_rows, 1)
        score += max(0.0, 0.35 * (1.0 - row_diff / max_rows))
    
    # Columns
    input_cols = input_main.get("cols", 0)
    template_cols = template_main.get("cols", 0)
    if input_cols == template_cols:
        score += 0.35
    else:
        col_diff = abs(input_cols - template_cols)
        max_cols = max(input_cols, template_cols, 1)
        score += max(0.0, 0.35 * (1.0 - col_diff / max_cols))
    
    return score


def compare_sections(input: Dict, template: Dict) -> float:
    """Compare section presence and positions."""
    input_sections = input.get("sections", {})
    template_sections = template.get("sections", {})
    
    score = 0.0
    section_names = ["header", "consumption_table", "payment_info"]
    
    for section_name in section_names:
        input_present = input_sections.get(section_name, {}).get("present", False)
        template_present = template_sections.get(section_name, {}).get("present", False)
        
        if input_present == template_present:
            score += 1.0 / len(section_names)
    
    return score


def compare_layout(input: Dict, template: Dict) -> float:
    """Compare layout structure."""
    input_layout = input.get("layout", {})
    template_layout = template.get("layout", {})
    
    input_cols = input_layout.get("column_layout", "")
    template_cols = template_layout.get("column_layout", "")
    
    if input_cols == template_cols:
        return 1.0
    else:
        return 0.0

