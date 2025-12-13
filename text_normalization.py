"""
Text normalization module for cleaning and normalizing extracted text.
Handles Persian/Arabic text, numbers, and whitespace normalization.
"""
import re
import unicodedata
import arabic_reshaper
from bidi.algorithm import get_display
from typing import Optional


class TextNormalizer:
    """Normalize and clean extracted text."""
    
    def __init__(self, 
                 normalize_whitespace: bool = True,
                 remove_extra_spaces: bool = True,
                 normalize_persian_numbers: bool = True,
                 handle_bidi: bool = True):
        """
        Initialize text normalizer.
        
        Args:
            normalize_whitespace: Normalize different whitespace characters
            remove_extra_spaces: Remove multiple consecutive spaces
            normalize_persian_numbers: Convert Persian digits to ASCII
            handle_bidi: Apply bidirectional text handling for RTL languages
        """
        self.normalize_whitespace = normalize_whitespace
        self.remove_extra_spaces = remove_extra_spaces
        self.normalize_persian_numbers = normalize_persian_numbers
        self.handle_bidi = handle_bidi
        
        # Persian/Arabic digit mapping
        self.persian_digits = "۰۱۲۳۴۵۶۷۸۹"
        self.arabic_digits = "٠١٢٣٤٥٦٧٨٩"
        self.ascii_digits = "0123456789"
    
    def normalize_persian_digits(self, text: str) -> str:
        """Convert Persian and Arabic digits to ASCII."""
        if not text:
            return text
        
        # Map Persian digits
        persian_map = str.maketrans(self.persian_digits, self.ascii_digits)
        text = text.translate(persian_map)
        
        # Map Arabic digits
        arabic_map = str.maketrans(self.arabic_digits, self.ascii_digits)
        text = text.translate(arabic_map)
        
        return text
    
    def normalize_whitespace_chars(self, text: str) -> str:
        """Normalize various whitespace characters to standard space."""
        if not text:
            return text
        
        # Replace various whitespace characters with standard space
        text = re.sub(r'[\u2000-\u200B\u202F\u205F\u3000]', ' ', text)
        # Replace zero-width characters
        text = re.sub(r'[\u200C\u200D\uFEFF]', '', text)
        # Normalize line breaks
        text = re.sub(r'\r\n', '\n', text)
        text = re.sub(r'\r', '\n', text)
        
        return text
    
    def remove_consecutive_spaces(self, text: str) -> str:
        """Remove multiple consecutive spaces."""
        if not text:
            return text
        return re.sub(r' +', ' ', text)
    
    def normalize_presentation_forms(self, text: str) -> str:
        """normalize presentation forms to standard characters (NFKC)."""
        if not text:
            return text
        return unicodedata.normalize('NFKC', text)
    
    def standardize_persian_chars(self, text: str) -> str:
        """Standardize Arabic/Persian characters (Yeh/Kaf) to Persian standard."""
        if not text:
            return text
        
        # Arabic Yeh -> Persian Yeh
        text = text.replace('ي', 'ی')
        text = text.replace('ى', 'ی')
        
        # Arabic Kaf -> Persian Kaf
        text = text.replace('ك', 'ک')
        
        # Heh with Hamza (can vary) -> Heh + Hamza or Yeh
        # text = text.replace('ۀ', 'ه') # Optional depending on preference
        
        return text
    
    def apply_bidi(self, text: str) -> str:
        """Apply bidirectional text algorithm for RTL languages."""
        if not text or not self.handle_bidi:
            return text
        
        try:
            # Don't reshape - just apply BIDI algorithm to convert visual to logical order
            # Reshaping causes garbled text, but BIDI algorithm fixes character order
            bidi_text = get_display(text)
            return bidi_text
        except Exception:
            # If BIDI fails, return original text
            return text
    
    def normalize(self, text: str, apply_bidi: Optional[bool] = None) -> str:
        """
        Apply all normalization steps to text.
        
        Args:
            text: Input text to normalize
            apply_bidi: Override handle_bidi setting (None uses instance setting)
        
        Returns:
            Normalized text
        """
        if not text:
            return text
        
        result = text
        
        # Normalize whitespace characters
        if self.normalize_whitespace:
            result = self.normalize_whitespace_chars(result)
        
        # Normalize Persian/Arabic digits
        if self.normalize_persian_numbers:
            result = self.normalize_persian_digits(result)
            
        # Normalize Presentation Forms (NFKC)
        result = self.normalize_presentation_forms(result)
        
        # Standardize Persian Characters (Yeh/Kaf)
        result = self.standardize_persian_chars(result)
        
        # Remove extra spaces
        if self.remove_extra_spaces:
            result = self.remove_consecutive_spaces(result)
            # Also clean up spaces around line breaks
            result = re.sub(r' *\n *', '\n', result)
            result = result.strip()
        
        # Apply bidirectional text handling
        use_bidi = apply_bidi if apply_bidi is not None else self.handle_bidi
        if use_bidi:
            result = self.apply_bidi(result)
        
        return result
    
    def normalize_table_cell(self, cell_text: str) -> str:
        """Normalize text from a table cell (preserves structure)."""
        if not cell_text:
            return ""
        
        # Normalize but don't apply BIDI to individual cells
        # (BIDI should be applied at display level)
        result = self.normalize(cell_text, apply_bidi=False)
        return result.strip()


# Default normalizer instance
default_normalizer = TextNormalizer()
