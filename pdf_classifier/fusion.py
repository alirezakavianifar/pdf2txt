"""
Fusion Module

Combines results from multiple detection modules.
"""

from pathlib import Path
from typing import Dict, List, Optional, Tuple
import json
from functools import lru_cache
from .cache import get_cache


@lru_cache(maxsize=1)
def _load_templates_db_cached(signatures_dir_str: str) -> Dict:
    """Cached version of load_templates_db."""
    signatures_dir = Path(signatures_dir_str)
    templates_db = {}
    
    signature_files = sorted(signatures_dir.glob("template_*.json"))
    
    for sig_file in signature_files:
        with open(sig_file, 'r', encoding='utf-8') as f:
            template_data = json.load(f)
            template_id = template_data.get("template_id")
            if template_id:
                templates_db[template_id] = template_data
    
    return templates_db


def load_templates_db(signatures_dir: Path = Path("templates_config/signatures")) -> Dict:
    """
    Load all template signatures from JSON files (with caching).
    
    Args:
        signatures_dir: Directory containing signature JSON files
    
    Returns:
        Dictionary mapping template_id to signature data
    """
    # Try cache first
    cache = get_cache()
    cached_db = cache.get_template_db()
    if cached_db is not None:
        return cached_db
    
    # Load from disk
    templates_db = _load_templates_db_cached(str(signatures_dir))
    
    # Cache it
    cache.cache_template_db(templates_db)
    
    return templates_db


def fuse_results(
    visual_scores: Dict[str, float],
    structure_scores: Dict[str, float],
    excluded_templates: List[str],
    confidence_threshold: float = 0.5,
    visual_weight: float = 0.6,
    structure_weight: float = 0.4,
    early_exit_threshold: float = 0.95
) -> Tuple[str, float, Dict]:
    """
    Fuse detection results from multiple modules.
    
    Args:
        visual_scores: Dictionary of template_id -> visual confidence
        structure_scores: Dictionary of template_id -> structure confidence
        excluded_templates: List of template IDs to exclude
        confidence_threshold: Minimum confidence to accept
        visual_weight: Weight for visual scores
        structure_weight: Weight for structure scores
        early_exit_threshold: High confidence threshold for early exit
    
    Returns:
        (template_id, confidence_score, details_dict)
    """
    # Get all template IDs
    all_template_ids = set(visual_scores.keys()) | set(structure_scores.keys())
    
    # Remove excluded templates
    valid_template_ids = all_template_ids - set(excluded_templates)
    
    if not valid_template_ids:
        return "unknown_template", 0.0, {
            "visual_score": 0.0,
            "structure_score": 0.0,
            "excluded_templates": excluded_templates,
            "warnings": ["All templates excluded by text detection"]
        }
    
    # Calculate fused scores
    fused_scores = {}
    
    for template_id in valid_template_ids:
        visual_score = visual_scores.get(template_id, 0.0)
        structure_score = structure_scores.get(template_id, 0.0)
        
        # Weighted combination
        fused_score = (
            visual_score * visual_weight +
            structure_score * structure_weight
        )
        
        fused_scores[template_id] = fused_score
    
    # Find best match
    if not fused_scores:
        return "unknown_template", 0.0, {
            "visual_score": 0.0,
            "structure_score": 0.0,
            "excluded_templates": excluded_templates,
            "warnings": ["No valid templates found"]
        }
    
    # Sort by score
    sorted_templates = sorted(
        fused_scores.items(),
        key=lambda x: x[1],
        reverse=True
    )
    
    best_template_id, best_score = sorted_templates[0]
    
    # Early exit: If very high confidence and structure matches well
    if len(sorted_templates) > 0:
        best_visual = visual_scores.get(best_template_id, 0.0)
        best_structure = structure_scores.get(best_template_id, 0.0)
        
        if best_score >= early_exit_threshold and best_structure >= 0.8:
            # High confidence, can return early
            pass  # Continue to normal return
    
    # Check for ambiguity
    warnings = []
    if len(sorted_templates) > 1:
        second_best_score = sorted_templates[1][1]
        score_difference = best_score - second_best_score
        
        if score_difference < 0.15:
            warnings.append(
                f"Ambiguous detection: {best_template_id} ({best_score:.3f}) vs "
                f"{sorted_templates[1][0]} ({second_best_score:.3f})"
            )
    
    # Check confidence threshold
    if best_score < confidence_threshold:
        return "unknown_template", best_score, {
            "visual_score": visual_scores.get(best_template_id, 0.0),
            "structure_score": structure_scores.get(best_template_id, 0.0),
            "excluded_templates": excluded_templates,
            "warnings": warnings + [f"Confidence {best_score:.3f} below threshold {confidence_threshold}"]
        }
    
    # Prepare details
    details = {
        "visual_score": visual_scores.get(best_template_id, 0.0),
        "structure_score": structure_scores.get(best_template_id, 0.0),
        "excluded_templates": excluded_templates,
        "warnings": warnings
    }
    
    # Add region scores if available (for debugging)
    if len(sorted_templates) > 1:
        details["top_candidates"] = [
            {"template_id": tid, "score": score}
            for tid, score in sorted_templates[:3]
        ]
    
    return best_template_id, best_score, details

