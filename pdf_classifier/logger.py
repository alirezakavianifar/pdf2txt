"""
Logging Module for Template Detection

Simplified logging for template detection operations.
"""

from pathlib import Path
from typing import Dict, Optional


class DetectionLogger:
    """Simplified logger for template detection operations."""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.stats = {
            "total_detections": 0,
            "successful_detections": 0,
            "unknown_template_count": 0,
            "low_confidence_count": 0,
            "errors": 0
        }
    
    def log_detection(
        self,
        pdf_path: Path,
        template_id: str,
        confidence: float,
        details: Dict,
        processing_time: Optional[float] = None
    ):
        """Log a detection result."""
        self.stats["total_detections"] += 1
        
        if template_id == "unknown_template":
            self.stats["unknown_template_count"] += 1
            if self.verbose:
                print(f"[WARN] Unknown template: {pdf_path.name} (confidence: {confidence:.3f})")
        elif confidence < 0.5:
            self.stats["low_confidence_count"] += 1
            if self.verbose:
                print(f"[WARN] Low confidence: {pdf_path.name} -> {template_id} (confidence: {confidence:.3f})")
        else:
            self.stats["successful_detections"] += 1
            if self.verbose:
                print(f"[OK] Detection: {pdf_path.name} -> {template_id} (confidence: {confidence:.3f})")
        
        # Log warnings if any
        if self.verbose and details.get("warnings"):
            for warning in details["warnings"]:
                print(f"  Warning: {warning}")
    
    def log_error(self, pdf_path: Path, error: Exception):
        """Log an error."""
        self.stats["errors"] += 1
        if self.verbose:
            print(f"[ERROR] Error processing {pdf_path.name}: {error}")
    
    def get_statistics(self) -> Dict:
        """Get detection statistics."""
        return self.stats.copy()


# Global logger instance
_global_logger = None


def get_logger(verbose: bool = False) -> DetectionLogger:
    """Get global logger instance."""
    global _global_logger
    if _global_logger is None:
        _global_logger = DetectionLogger(verbose=verbose)
    return _global_logger

