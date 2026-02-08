"""
Template Signature Generator

Generates signature JSON files for PDF templates that can be used by the classifier.
"""

from pathlib import Path
from typing import Dict, List, Tuple
import json
import numpy as np
import cv2
import imagehash
from PIL import Image
import fitz  # PyMuPDF

from .visual_detector import render_and_preprocess, extract_regions, preprocess_image
from .structure_detector import extract_structural_features
from .text_detector import extract_text_from_pdf, normalize_persian_text


def generate_template_signature(
    pdf_path: Path,
    template_id: str,
    template_file: str = None,
    output_dir: Path = None,
    dpi: int = 300
) -> Dict:
    """
    Generate a complete template signature from a PDF file.
    
    Args:
        pdf_path: Path to the reference PDF file
        template_id: Template identifier (e.g., "template_9")
        template_file: Relative path to template file (for reference)
        output_dir: Directory to save signature JSON (default: templates_config/signatures)
        dpi: DPI for rendering (default: 300)
    
    Returns:
        Dictionary containing the complete signature
    """
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    
    print(f"Generating signature for {template_id} from {pdf_path.name}...")
    
    # Generate visual signature
    print("  Extracting visual features...")
    visual_sig = generate_visual_signature(pdf_path, dpi)
    
    # Generate structural signature
    print("  Extracting structural features...")
    structural_sig = extract_structural_features(pdf_path)
    
    # Generate text signature (for exclusion keywords)
    print("  Extracting text features...")
    text_sig = generate_text_signature(pdf_path)
    
    # Build complete signature
    signature = {
        "template_id": template_id,
        "template_file": template_file or str(pdf_path),
        "signatures": {
            "visual": visual_sig,
            "structural": structural_sig,
            "text": text_sig
        }
    }
    
    # Save to file
    if output_dir is None:
        package_dir = Path(__file__).parent
        output_dir = package_dir / "templates_config" / "signatures"
    
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f"{template_id}.json"
    
    print(f"  Saving signature to {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(signature, f, indent=2, ensure_ascii=False)
    
    print(f"[OK] Signature generated successfully: {output_file}")
    return signature


def generate_visual_signature(pdf_path: Path, dpi: int = 300) -> Dict:
    """
    Generate visual signature from PDF.
    
    Returns:
        Dictionary with visual signature data
    """
    # Render and preprocess
    img_gray, page_width, page_height = render_and_preprocess(pdf_path, dpi)
    
    if img_gray is None:
        raise ValueError(f"Failed to render PDF: {pdf_path}")
    
    # Extract regions
    regions = extract_regions(img_gray, page_width, page_height)
    
    # Generate signatures for each region
    visual_sig = {
        "regions": {}
    }
    
    region_names = ["header", "main_table", "payment_info"]
    
    for region_name in region_names:
        if region_name in regions:
            region_img = regions[region_name]
            region_sig = generate_region_signature(region_img, page_width, page_height, region_name)
            visual_sig["regions"][region_name] = region_sig
    
    # Add page metadata
    visual_sig["page_dimensions"] = [int(page_width), int(page_height)]
    visual_sig["preprocessing_applied"] = True
    
    return visual_sig


def generate_region_signature(
    region_img: np.ndarray,
    page_width: int,
    page_height: int,
    region_name: str
) -> Dict:
    """
    Generate signature for a single region.
    
    Args:
        region_img: Grayscale image array of the region
        page_width: Full page width
        page_height: Full page height
        region_name: Name of the region
    
    Returns:
        Dictionary with region signature (bbox, hashes, histogram)
    """
    # Calculate bounding box (normalized and pixel coordinates)
    region_height, region_width = region_img.shape
    
    # Default region coordinates based on region name
    if region_name == "header":
        bbox_norm = [0.0, 0.0, 1.0, 0.25]
        bbox_pixels = [0, 0, int(page_width), int(page_height * 0.25)]
    elif region_name == "main_table":
        bbox_norm = [0.1, 0.25, 0.9, 0.65]
        x_start = int(page_width * 0.1)
        x_end = int(page_width * 0.9)
        y_start = int(page_height * 0.25)
        y_end = int(page_height * 0.65)
        bbox_pixels = [x_start, y_start, x_end, y_end]
    elif region_name == "payment_info":
        bbox_norm = [0.1, 0.7, 0.9, 0.95]
        x_start = int(page_width * 0.1)
        x_end = int(page_width * 0.9)
        y_start = int(page_height * 0.7)
        y_end = int(page_height * 0.95)
        bbox_pixels = [x_start, y_start, x_end, y_end]
    else:
        # Default to full region
        bbox_norm = [0.0, 0.0, 1.0, 1.0]
        bbox_pixels = [0, 0, int(page_width), int(page_height)]
    
    # Convert to PIL Image for hashing
    region_pil = Image.fromarray(region_img)
    # Resize to standard size for consistent hashing
    region_pil_resized = region_pil.resize((512, 512), Image.Resampling.LANCZOS)
    
    # Calculate hashes
    hashes = {}
    try:
        hashes["phash"] = str(imagehash.phash(region_pil_resized, hash_size=16))
    except Exception as e:
        print(f"    Warning: Failed to calculate pHash: {e}")
    
    try:
        hashes["dhash"] = str(imagehash.dhash(region_pil_resized, hash_size=8))
    except Exception as e:
        print(f"    Warning: Failed to calculate dHash: {e}")
    
    try:
        hashes["ahash"] = str(imagehash.average_hash(region_pil_resized, hash_size=8))
    except Exception as e:
        print(f"    Warning: Failed to calculate aHash: {e}")
    
    try:
        hashes["whash"] = str(imagehash.whash(region_pil_resized, hash_size=8))
    except Exception as e:
        print(f"    Warning: Failed to calculate wHash: {e}")
    
    # Calculate histogram
    histogram = cv2.calcHist([region_img], [0], None, [256], [0, 256]).flatten().tolist()
    
    # Build region signature
    region_sig = {
        "bbox_norm": bbox_norm,
        "bbox_pixels": bbox_pixels,
        "hashes": hashes,
        "histogram": histogram
    }
    
    return region_sig


def generate_text_signature(pdf_path: Path) -> Dict:
    """
    Generate text signature for exclusion keywords.
    
    Note: This is for exclusion only, not positive identification.
    Users can manually add exclusion keywords if needed.
    
    Returns:
        Dictionary with text signature
    """
    text = extract_text_from_pdf(pdf_path)
    
    # For now, return empty exclusion keywords
    # Users can manually add keywords that would indicate this is NOT the template
    text_sig = {
        "exclusion_keywords": [],
        "unique_text_patterns": [],
        "note": "Text is NOT used for positive identification, only exclusion"
    }
    
    return text_sig


def main():
    """Command-line interface for signature generation."""
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Generate template signature from PDF file"
    )
    parser.add_argument(
        "pdf_path",
        type=Path,
        help="Path to PDF file"
    )
    parser.add_argument(
        "--template-id",
        type=str,
        required=True,
        help="Template ID (e.g., template_9)"
    )
    parser.add_argument(
        "--template-file",
        type=str,
        default=None,
        help="Relative path to template file (for reference)"
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Output directory for signature JSON (default: templates_config/signatures)"
    )
    parser.add_argument(
        "--dpi",
        type=int,
        default=300,
        help="DPI for rendering (default: 300)"
    )
    
    args = parser.parse_args()
    
    try:
        signature = generate_template_signature(
            pdf_path=args.pdf_path,
            template_id=args.template_id,
            template_file=args.template_file,
            output_dir=args.output_dir,
            dpi=args.dpi
        )
        print("\n[OK] Signature generation completed successfully!")
        print(f"  Template ID: {signature['template_id']}")
        print(f"  Visual regions: {list(signature['signatures']['visual']['regions'].keys())}")
        print(f"  Pages: {signature['signatures']['structural']['num_pages']}")
        return 0
    except Exception as e:
        print(f"\n[ERROR] {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
