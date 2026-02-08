"""
PDF Template Classifier

A self-contained module for classifying PDFs by template using visual,
structural, and text-based detection methods.
"""

from pathlib import Path
from typing import Dict, Optional, Tuple
import time
import sys
from .text_detector import detect_by_text
from .visual_detector import detect_by_visual
from .structure_detector import detect_by_structure
from .fusion import fuse_results, load_templates_db
from .logger import get_logger


def detect_template(
    pdf_path: Path,
    templates_db: Optional[Dict] = None,
    signatures_dir: Optional[Path] = None,
    confidence_threshold: float = 0.5,
    use_text_exclusion: bool = True,
    use_visual: bool = True,
    use_structure: bool = True
) -> Tuple[str, float, Dict]:
    """
    Detect which template a PDF belongs to.
    
    Args:
        pdf_path: Path to PDF file
        templates_db: Pre-loaded templates database (optional)
        signatures_dir: Directory containing template signature JSON files
                       (default: looks for templates_config/signatures relative to this package)
        confidence_threshold: Minimum confidence to accept detection
        use_text_exclusion: Use text for exclusion (default: True)
        use_visual: Use visual detection (default: True)
        use_structure: Use structural detection (default: True)
    
    Returns:
        (template_id, confidence_score, details_dict)
        - template_id: "template_X" or "unknown_template"
        - confidence_score: 0.0 to 1.0
        - details_dict: {
            "visual_score": 0.7,
            "structure_score": 0.6,
            "excluded_templates": [...],
            "region_scores": {...},
            "structural_matches": {...},
            "warnings": [...]
          }
    
    Example:
        >>> from pathlib import Path
        >>> from pdf_classifier import detect_template
        >>> 
        >>> pdf_path = Path("document.pdf")
        >>> template_id, confidence, details = detect_template(pdf_path)
        >>> print(f"Template: {template_id}, Confidence: {confidence:.2f}")
    """
    # Load templates if not provided
    if templates_db is None:
        if signatures_dir is None:
            # Try to find signatures relative to this package
            # For PyInstaller executables, use _MEIPASS
            if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
                # Running in a PyInstaller bundle
                base_dir = Path(sys._MEIPASS)
                signatures_dir = base_dir / "pdf_classifier" / "templates_config" / "signatures"
                print(f"[DEBUG] Running in PyInstaller bundle, signatures_dir: {signatures_dir}")
                print(f"[DEBUG] Signatures directory exists: {signatures_dir.exists()}")
            else:
                # Running in normal Python environment
                package_dir = Path(__file__).parent
                signatures_dir = package_dir / "templates_config" / "signatures"
                if not signatures_dir.exists():
                    # Fallback: try parent directory
                    signatures_dir = package_dir.parent / "templates_config" / "signatures"
                print(f"[DEBUG] Running in normal Python, signatures_dir: {signatures_dir}")
                print(f"[DEBUG] Signatures directory exists: {signatures_dir.exists()}")
        
        templates_db = load_templates_db(signatures_dir)
    
    # Start timing
    start_time = time.time()
    
    # Get logger
    logger = get_logger()
    
    try:
        # Run detection modules
        excluded_templates = []
        visual_scores = {}
        structure_scores = {}
        
        # Text-based exclusion
        if use_text_exclusion:
            excluded_templates = detect_by_text(pdf_path, templates_db)
        
        # Visual detection (PRIMARY)
        if use_visual:
            visual_scores = detect_by_visual(pdf_path, templates_db, use_cache=True)
        
        # Structural detection (PRIMARY)
        if use_structure:
            structure_scores = detect_by_structure(pdf_path, templates_db)
        
        # Fuse results
        template_id, confidence, details = fuse_results(
            visual_scores=visual_scores,
            structure_scores=structure_scores,
            excluded_templates=excluded_templates,
            confidence_threshold=confidence_threshold
        )
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Log detection
        logger.log_detection(
            pdf_path,
            template_id,
            confidence,
            details,
            processing_time
        )
        
        return template_id, confidence, details
    
    except Exception as e:
        processing_time = time.time() - start_time
        logger.log_error(pdf_path, e)
        raise


__all__ = ['detect_template', 'load_templates_db']

# Export signature generation functions for convenience
try:
    from .generate_signature import generate_template_signature
    from .generate_signatures_batch import generate_signatures_batch
    __all__.extend(['generate_template_signature', 'generate_signatures_batch'])
except ImportError:
    # Signature generation is optional
    pass
