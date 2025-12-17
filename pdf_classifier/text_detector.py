"""
Text-Based Detection Module (EXCLUSION ONLY)

This module is used ONLY for exclusion, not positive identification.
"""

from pathlib import Path
from typing import Dict, List, Set
import fitz  # PyMuPDF
import re


def detect_by_text(pdf_path: Path, templates_db: Dict) -> List[str]:
    """
    Detect templates to exclude based on text content.
    
    Args:
        pdf_path: Path to PDF file
        templates_db: Templates database with signatures
    
    Returns:
        List of template IDs that should be excluded (empty if none)
    """
    excluded_templates = []
    
    # Extract text from PDF
    text = extract_text_from_pdf(pdf_path)
    
    if not text:
        # No text available, skip exclusion
        return excluded_templates
    
    # Normalize text
    text_normalized = normalize_persian_text(text)
    
    # Check each template for exclusion keywords
    for template_id, template_sig in templates_db.items():
        text_sig = template_sig.get("signatures", {}).get("text", {})
        exclusion_keywords = text_sig.get("exclusion_keywords", [])
        unique_patterns = text_sig.get("unique_text_patterns", [])
        
        # Check exclusion keywords
        for keyword in exclusion_keywords:
            if keyword and keyword in text_normalized:
                excluded_templates.append(template_id)
                break  # One exclusion keyword is enough
        
        # Check unique patterns (if any)
        for pattern in unique_patterns:
            if pattern and re.search(pattern, text_normalized):
                # This pattern indicates this is NOT the template
                # (if pattern matches, exclude)
                excluded_templates.append(template_id)
                break
    
    return list(set(excluded_templates))  # Remove duplicates


def extract_text_from_pdf(pdf_path: Path) -> str:
    """
    Extract text from PDF first page.
    
    Args:
        pdf_path: Path to PDF file
    
    Returns:
        Extracted text (empty string if no text available)
    """
    try:
        doc = fitz.open(pdf_path)
        if len(doc) == 0:
            return ""
        
        # Extract text from first page
        page = doc[0]
        text = page.get_text()
        
        doc.close()
        return text
    except Exception:
        # If extraction fails, return empty string
        return ""


def normalize_persian_text(text: str) -> str:
    """
    Normalize Persian text for comparison.
    
    Args:
        text: Raw text
    
    Returns:
        Normalized text
    """
    # Convert to lowercase
    text = text.lower()
    
    # Remove diacritics (optional - Persian text may not have many)
    # Normalize Arabic/Persian character variants
    # ی and ي
    text = text.replace('ي', 'ی')
    # ک and ك
    text = text.replace('ك', 'ک')
    
    # Remove extra whitespace
    text = ' '.join(text.split())
    
    return text

