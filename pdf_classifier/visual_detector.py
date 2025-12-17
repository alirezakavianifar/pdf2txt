"""
Visual-Based Detection Module (PRIMARY)

Optimized visual detection using multiple hash algorithms, histograms,
and feature matching.
"""

from pathlib import Path
from typing import Dict, Optional, Tuple
import numpy as np
import cv2
import imagehash
from PIL import Image
import fitz  # PyMuPDF
from .cache import get_cache


def detect_by_visual(
    pdf_path: Path,
    templates_db: Dict,
    use_cache: bool = True,
    parallel: bool = False,  # Can be enabled later
    quality_threshold: float = 0.3
) -> Dict[str, float]:
    """
    Detect template using visual features.
    
    Args:
        pdf_path: Path to PDF file
        templates_db: Templates database with signatures
        use_cache: Use caching
        parallel: Use parallel processing (not implemented yet)
        quality_threshold: Minimum quality threshold
    
    Returns:
        Dictionary mapping template_id to confidence score
    """
    cache = get_cache() if use_cache else None
    
    # Try to get cached image
    if cache:
        cached_image = cache.get_cached_image(pdf_path)
        if cached_image:
            img_gray, page_width, page_height = cached_image
        else:
            img_gray, page_width, page_height = render_and_preprocess(pdf_path)
            if img_gray is not None:
                cache.cache_image(pdf_path, (img_gray, page_width, page_height))
    else:
        img_gray, page_width, page_height = render_and_preprocess(pdf_path)
    
    if img_gray is None:
        return {}
    
    # Try to get cached regions
    if cache:
        cached_regions = cache.get_cached_regions(pdf_path)
        if cached_regions:
            input_regions = cached_regions
        else:
            input_regions = extract_regions(img_gray, page_width, page_height)
            cache.cache_regions(pdf_path, input_regions)
    else:
        input_regions = extract_regions(img_gray, page_width, page_height)
    
    # Compare with each template
    visual_scores = {}
    
    for template_id, template_sig in templates_db.items():
        visual_sig = template_sig.get("signatures", {}).get("visual", {})
        template_regions = visual_sig.get("regions", {})
        
        if not template_regions:
            continue
        
        # Calculate region scores
        region_scores = {}
        
        for region_name in ["header", "main_table", "payment_info"]:
            if region_name in input_regions and region_name in template_regions:
                score = compare_region(
                    input_regions[region_name],
                    template_regions[region_name]
                )
                region_scores[region_name] = score
        
        # Calculate final visual confidence
        visual_confidence = calculate_visual_confidence(region_scores)
        visual_scores[template_id] = visual_confidence
    
    return visual_scores


def render_and_preprocess(pdf_path: Path, dpi: int = 300) -> Tuple[Optional[np.ndarray], int, int]:
    """
    Render PDF first page and preprocess image.
    
    Returns:
        (preprocessed_image, page_width, page_height) or (None, 0, 0) on error
    """
    try:
        doc = fitz.open(pdf_path)
        if len(doc) == 0:
            return None, 0, 0
        
        page = doc[0]
        
        # Render at specified DPI
        mat = fitz.Matrix(dpi / 72, dpi / 72)
        pix = page.get_pixmap(matrix=mat)
        
        # Convert to numpy array
        img_array = np.frombuffer(pix.samples, dtype=np.uint8).reshape(
            pix.height, pix.width, pix.n
        )
        
        # Convert to grayscale
        if pix.n == 4:  # RGBA
            img = Image.fromarray(img_array, 'RGBA').convert('RGB')
        else:  # RGB
            img = Image.fromarray(img_array, 'RGB')
        
        img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        img_gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
        
        # Preprocess
        img_processed = preprocess_image(img_gray)
        
        doc.close()
        
        return img_processed, pix.width, pix.height
    except Exception as e:
        print(f"[ERROR] Failed to render PDF {pdf_path}: {e}")
        return None, 0, 0


def preprocess_image(img_gray: np.ndarray) -> np.ndarray:
    """Apply preprocessing pipeline to image."""
    # CLAHE for contrast enhancement
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    img = clahe.apply(img_gray)
    
    # Mild Gaussian blur for noise reduction
    img = cv2.GaussianBlur(img, (3, 3), 0)
    
    return img


def extract_regions(
    img_gray: np.ndarray,
    page_width: int,
    page_height: int
) -> Dict[str, np.ndarray]:
    """Extract regions from image using default coordinates."""
    regions = {}
    
    # Header region (top 25%)
    header = img_gray[0:int(page_height * 0.25), :]
    if header.size > 0:
        regions["header"] = header
    
    # Main table region (middle section)
    y_start = int(page_height * 0.25)
    y_end = int(page_height * 0.65)
    x_start = int(page_width * 0.1)
    x_end = int(page_width * 0.9)
    main_table = img_gray[y_start:y_end, x_start:x_end]
    if main_table.size > 0:
        regions["main_table"] = main_table
    
    # Payment info region (bottom section)
    y_start = int(page_height * 0.7)
    y_end = int(page_height * 0.95)
    payment_info = img_gray[y_start:y_end, :]
    if payment_info.size > 0:
        regions["payment_info"] = payment_info
    
    return regions


def compare_region(
    input_region: np.ndarray,
    template_region_data: Dict
) -> float:
    """
    Compare input region with template region.
    
    Returns:
        Similarity score (0.0 to 1.0)
    """
    # Get template hashes
    template_hashes = template_region_data.get("hashes", {})
    template_histogram = np.array(template_region_data.get("histogram", []))
    
    # Calculate input hashes
    input_img_pil = Image.fromarray(input_region)
    input_img_pil = input_img_pil.resize((512, 512), Image.Resampling.LANCZOS)
    
    # Hash comparison
    hash_scores = []
    
    # pHash
    if template_hashes.get("phash"):
        try:
            template_phash = imagehash.hex_to_hash(template_hashes["phash"])
            input_phash = imagehash.phash(input_img_pil, hash_size=16)
            phash_dist = template_phash - input_phash
            phash_sim = 1.0 - (phash_dist / 256.0)
            phash_sim = max(0.0, min(1.0, phash_sim))
            hash_scores.append(("phash", phash_sim, 0.35))
        except Exception:
            pass
    
    # dHash
    if template_hashes.get("dhash"):
        try:
            template_dhash = imagehash.hex_to_hash(template_hashes["dhash"])
            input_dhash = imagehash.dhash(input_img_pil, hash_size=8)
            dhash_dist = template_dhash - input_dhash
            dhash_sim = 1.0 - (dhash_dist / 72.0)
            dhash_sim = max(0.0, min(1.0, dhash_sim))
            hash_scores.append(("dhash", dhash_sim, 0.30))
        except Exception:
            pass
    
    # aHash
    if template_hashes.get("ahash"):
        try:
            template_ahash = imagehash.hex_to_hash(template_hashes["ahash"])
            input_ahash = imagehash.average_hash(input_img_pil, hash_size=8)
            ahash_dist = template_ahash - input_ahash
            ahash_sim = 1.0 - (ahash_dist / 64.0)
            ahash_sim = max(0.0, min(1.0, ahash_sim))
            hash_scores.append(("ahash", ahash_sim, 0.20))
        except Exception:
            pass
    
    # wHash
    if template_hashes.get("whash"):
        try:
            template_whash = imagehash.hex_to_hash(template_hashes["whash"])
            input_whash = imagehash.whash(input_img_pil, hash_size=8)
            whash_dist = template_whash - input_whash
            whash_sim = 1.0 - (whash_dist / 64.0)  # Approximate
            whash_sim = max(0.0, min(1.0, whash_sim))
            hash_scores.append(("whash", whash_sim, 0.15))
        except Exception:
            pass
    
    # Calculate weighted hash score
    if hash_scores:
        total_weight = sum(w for _, _, w in hash_scores)
        if total_weight > 0:
            hash_score = sum(sim * weight for _, sim, weight in hash_scores) / total_weight
        else:
            hash_score = 0.0
    else:
        hash_score = 0.0
    
    # Histogram comparison
    stat_score = 0.0
    if len(template_histogram) > 0:
        try:
            input_hist = cv2.calcHist([input_region], [0], None, [256], [0, 256]).flatten()
            # Normalize histograms
            input_hist = input_hist / (input_hist.sum() + 1e-10)
            template_hist = template_histogram / (template_histogram.sum() + 1e-10)
            
            # Correlation coefficient
            correlation = cv2.compareHist(
                input_hist.astype(np.float32),
                template_hist.astype(np.float32),
                cv2.HISTCMP_CORREL
            )
            stat_score = max(0.0, correlation)
        except Exception:
            pass
    
    # Combine hash and statistical scores
    # Hash: 60%, Statistical: 25%, Feature: 15% (feature not implemented yet)
    region_score = hash_score * 0.60 + stat_score * 0.25
    
    return region_score


def calculate_visual_confidence(region_scores: Dict[str, float]) -> float:
    """
    Calculate final visual confidence from region scores.
    
    Args:
        region_scores: Dictionary of region_name -> score
    
    Returns:
        Final visual confidence (0.0 to 1.0)
    """
    if not region_scores:
        return 0.0
    
    # Weighted average
    weights = {
        "header": 0.40,
        "main_table": 0.35,
        "payment_info": 0.15,
        "logo": 0.10
    }
    
    total_score = 0.0
    total_weight = 0.0
    
    for region_name, score in region_scores.items():
        weight = weights.get(region_name, 0.1)
        total_score += score * weight
        total_weight += weight
    
    if total_weight > 0:
        return total_score / total_weight
    else:
        return 0.0

